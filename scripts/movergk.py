#!/usr/bin/env python3

# import rclpy
# from rclpy.node import Node
# from std_msgs.msg import Float64
# from nav_msgs.msg import Odometry
# import threading
# import math

# class GlobalCoordinateController(Node):
#     def __init__(self):
#         super().__init__('global_coord_controller')
        
#         # Parameter fisik robot
#         self.wheel_radius = 0.03
#         self.wheel_separation = 0.17
        
#         # Variabel State Robot
#         self.current_x = 0.0
#         self.current_y = 0.0
#         self.current_theta = 0.0
#         self.target_x = 0.0
#         self.target_y = 0.0
#         self.is_moving = False
        
#         # Publisher untuk roda
#         self.left_publisher = self.create_publisher(Float64, '/left_wheel/command', 10)
#         self.right_publisher = self.create_publisher(Float64, '/right_wheel/command', 10)
        
#         # Subscriber untuk Odometry (Mendapatkan Posisi Global)
#         self.create_subscription(Odometry, '/odom', self.odom_callback, 10)
        
#         # Timer untuk Control Loop (10 Hz)
#         self.timer = self.create_timer(0.1, self.control_loop)
        
#         self.get_logger().info('Global Coordinate Controller aktif. Menunggu posisi...')

#         # Menjalankan thread CLI
#         self.cli_thread = threading.Thread(target=self.input_loop)
#         self.cli_thread.daemon = True
#         self.cli_thread.start()

#     def odom_callback(self, msg):
#         # Mengambil posisi X dan Y global
#         self.current_x = msg.pose.pose.position.x
#         self.current_y = msg.pose.pose.position.y
        
#         # Mengonversi orientasi Quaternion ke Euler Angle (Yaw / Theta)
#         q = msg.pose.pose.orientation
#         self.current_theta = self.euler_from_quaternion(q.x, q.y, q.z, q.w)

#     def euler_from_quaternion(self, x, y, z, w):
#         # Konversi matematika dasar dari quaternion ke radian (yaw)
#         t3 = +2.0 * (w * z + x * y)
#         t4 = +1.0 - 2.0 * (y * y + z * z)
#         return math.atan2(t3, t4)

#     def input_loop(self):
#         # Jeda sejenak agar odometry masuk dulu
#         import time
#         time.sleep(2) 
        
#         while rclpy.ok():
#             try:
#                 print(f"\n[Posisi Saat Ini -> X: {self.current_x:.2f}, Y: {self.current_y:.2f}]")
#                 print("--- Input Koordinat Global Target ---")
#                 x = float(input("Masukkan Target X (meter) : "))
#                 y = float(input("Masukkan Target Y (meter) : "))
                
#                 self.target_x = x
#                 self.target_y = y
#                 self.is_moving = True
#                 self.get_logger().info(f'Berangkat menuju X: {x}, Y: {y} ...')
                
#             except ValueError:
#                 print("Input tidak valid. Harap masukkan angka.")
#             except EOFError:
#                 break

#     def control_loop(self):
#         if not self.is_moving:
#             return

#         # 1. Menghitung jarak ke target (Error Posisi)
#         dx = self.target_x - self.current_x
#         dy = self.target_y - self.current_y
#         distance = math.sqrt(dx**2 + dy**2)

#         # PERBAIKAN 1: Perbesar toleransi jarak menjadi 0.1 meter (10 cm) atau 0.15 meter
#         if distance < 0.1:
#             self.stop_robot()
#             self.is_moving = False
#             self.get_logger().info('*** Target Koordinat Tercapai! ***\n')
#             return

#         # 2. Menghitung sudut ke target (Error Sudut)
#         target_theta = math.atan2(dy, dx)
#         theta_error = target_theta - self.current_theta
        
#         # Normalisasi sudut agar selalu berada di antara -pi sampai pi
#         theta_error = math.atan2(math.sin(theta_error), math.cos(theta_error))

#         # PERBAIKAN 2: Turunkan sedikit nilai Kp agar pergerakan lebih halus
#         Kp_w = 1.0  # Konstanta belok (sebelumnya 1.5)
#         Kp_v = 0.3  # Konstanta maju (sebelumnya 0.5)

#         w = Kp_w * theta_error
#         v = Kp_v * distance

#         # Batasi kecepatan maksimal agar tidak terlalu melesat
#         if v > 0.3: v = 0.3 
        
#         # Jika robot belum menghadap target secara akurat (error sudut > 15 derajat / 0.26 rad), 
#         # utamakan berbelok di tempat perlahan, hentikan kecepatan maju
#         if abs(theta_error) > 0.26:
#             v = 0.0

#         # 4. Kirim ke Inverse Kinematics
#         self.calculate_and_publish(v, w)
        
#     def calculate_and_publish(self, v, w):
#         # Perhitungan Inverse Kinematics (Meneruskan perintah dari controller)
#         omega_l = (v - (w * self.wheel_separation / 2.0)) / self.wheel_radius
#         omega_r = (v + (w * self.wheel_separation / 2.0)) / self.wheel_radius

#         msg_left = Float64()
#         msg_right = Float64()
#         msg_left.data = omega_l
#         msg_right.data = omega_r

#         self.left_publisher.publish(msg_left)
#         self.right_publisher.publish(msg_right)

#     def stop_robot(self):
#         self.calculate_and_publish(0.0, 0.0)

# def main(args=None):
#     rclpy.init(args=args)
#     node = GlobalCoordinateController()
    
#     try:
#         rclpy.spin(node)
#     except KeyboardInterrupt:
#         pass
#     finally:
#         if rclpy.ok():
#             node.destroy_node()
#             rclpy.shutdown()

# if __name__ == '__main__':
#     main()


import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64
from nav_msgs.msg import Odometry
import threading
import math
import time

class GlobalCoordinateController(Node):
    def __init__(self):
        super().__init__('global_coord_controller')
        
        # Parameter fisik robot
        self.wheel_radius = 0.03
        self.wheel_separation = 0.17
        
        # Variabel State Robot
        self.current_x = 0.0
        self.current_y = 0.0
        self.current_theta = 0.0
        self.target_x = 0.0
        self.target_y = 0.0
        self.is_moving = False
        
        # Publisher untuk roda
        self.left_publisher = self.create_publisher(Float64, '/left_wheel/command', 10)
        self.right_publisher = self.create_publisher(Float64, '/right_wheel/command', 10)
        
        # Subscriber untuk Odometry (Mendapatkan Posisi Global)
        self.create_subscription(Odometry, '/odom', self.odom_callback, 10)
        
        # Timer untuk Control Loop (10 Hz)
        self.timer = self.create_timer(0.1, self.control_loop)
        
        self.get_logger().info('Global Coordinate Controller aktif. Menunggu posisi...')

        # Menjalankan thread CLI
        self.cli_thread = threading.Thread(target=self.input_loop)
        self.cli_thread.daemon = True
        self.cli_thread.start()

    def odom_callback(self, msg):
        # Mengambil posisi X dan Y global
        self.current_x = msg.pose.pose.position.x
        self.current_y = msg.pose.pose.position.y
        
        # Mengonversi orientasi Quaternion ke Euler Angle (Yaw / Theta)
        q = msg.pose.pose.orientation
        self.current_theta = self.euler_from_quaternion(q.x, q.y, q.z, q.w)

    def euler_from_quaternion(self, x, y, z, w):
        # Konversi matematika dasar dari quaternion ke radian (yaw)
        t3 = +2.0 * (w * z + x * y)
        t4 = +1.0 - 2.0 * (y * y + z * z)
        return math.atan2(t3, t4)

    def input_loop(self):
        # Jeda sejenak agar odometry masuk dulu
        time.sleep(2) 
        
        while rclpy.ok():
            try:
                while self.is_moving:
                    time.sleep(0.5)

                print(f"\n[Posisi Saat Ini -> X: {self.current_x:.2f}, Y: {self.current_y:.2f}]")
                print("--- Input Koordinat Global Target ---")
                x = float(input("Masukkan Target X (meter) : "))
                y = float(input("Masukkan Target Y (meter) : "))
                
                self.target_x = x
                self.target_y = y
                self.is_moving = True
                self.get_logger().info(f'Berangkat menuju X: {x}, Y: {y} ...')
                
            except ValueError:
                print("Input tidak valid. Harap masukkan angka.")
            except EOFError:
                break

    def control_loop(self):
        if not self.is_moving:
            return

        # 1. Menghitung jarak ke target (Error Posisi)
        dx = self.target_x - self.current_x
        dy = self.target_y - self.current_y
        distance = math.sqrt(dx**2 + dy**2)

        # Toleransi jarak menjadi 0.05 meter (5 cm)
        if distance < 0.05:
            self.stop_robot()
            self.is_moving = False
            
            print() 
            self.get_logger().info('*** Target Koordinat Tercapai! ***\n')
            return

        # 2. Menghitung sudut ke target (Error Sudut)
        target_theta = math.atan2(dy, dx)
        theta_error = target_theta - self.current_theta
        
        # Normalisasi sudut agar selalu berada di antara -pi sampai pi
        theta_error = math.atan2(math.sin(theta_error), math.cos(theta_error))

        # Konstanta Kp
        Kp_w = 1.0  
        Kp_v = 0.3  

        w = Kp_w * theta_error
        v = Kp_v * distance

        # Batasi kecepatan maksimal agar tidak terlalu melesat
        if v > 0.3: v = 0.3 
        
        # Utamakan berbelok di tempat perlahan jika error sudut > 15 derajat
        if abs(theta_error) > 0.26:
            v = 0.0

        # Menghitung kecepatan dalam koordinat global
        v_x_global = v * math.cos(self.current_theta)
        v_y_global = v * math.sin(self.current_theta)
        
        # --- PERUBAHAN BARU ---
        # Menggunakan \r untuk menggeser kursor ke ujung kiri baris yang sama.
        # Spasi ekstra di belakang ditambahkan agar sisa teks sebelumnya yang 
        # lebih panjang ikut terhapus secara visual.
        print(
            f'\rPos: ({self.current_x:.2f}, {self.current_y:.2f}) | '
            f'Sisa Jarak: {distance:.2f}m | '
            f'Vel Global: Vx={v_x_global:.2f}, Vy={v_y_global:.2f}    ',
            end='', flush=True
        )
        # ----------------------

        # 4. Kirim ke Inverse Kinematics
        self.calculate_and_publish(v, w)
        
    def calculate_and_publish(self, v, w):
        # Perhitungan Inverse Kinematics
        omega_l = (v - (w * self.wheel_separation / 2.0)) / self.wheel_radius
        omega_r = (v + (w * self.wheel_separation / 2.0)) / self.wheel_radius

        msg_left = Float64()
        msg_right = Float64()
        msg_left.data = omega_l
        msg_right.data = omega_r

        self.left_publisher.publish(msg_left)
        self.right_publisher.publish(msg_right)

    def stop_robot(self):
        self.calculate_and_publish(0.0, 0.0)

def main(args=None):
    rclpy.init(args=args)
    node = GlobalCoordinateController()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        if rclpy.ok():
            node.destroy_node()
            rclpy.shutdown()

if __name__ == '__main__':
    main()