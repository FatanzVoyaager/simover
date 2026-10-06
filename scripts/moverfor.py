#!/usr/bin/env python3

# import rclpy
# from rclpy.node import Node
# from geometry_msgs.msg import Twist
# import time

# class MoverNode(Node):
#     def __init__(self):
#         super().__init__('mover_node')
        
#         self.publisher_ = self.create_publisher(Twist, 'cmd_vel', 10)
        
#         self.timer = self.create_timer(0.1, self.timer_callback)
#         self.start_time = time.time()

#     def timer_callback(self):
#         msg = Twist()
#         current_time = time.time()
#         elapsed_time = current_time - self.start_time

#         if elapsed_time < 6.0:
#             msg.linear.x = 0.5   # Kecepatan linear (m/s)
#             msg.angular.z = 0.0
#             self.get_logger().info('Gerak Maju 6s')
#         elif elapsed_time < 9.0:
#             msg.linear.x = 0.0
#             msg.angular.z = -0.5236  # Kecepatan rotasi (rad/s)
#             self.get_logger().info('Rotasi Kanan 90 Derajat')
#         elif elapsed_time < 12.0:
#             msg.linear.x = 0.5 # Kecepatan linear (m/s)
#             msg.angular.z = 0.0  
#             self.get_logger().info('Gerak Maju 3s')
#         elif elapsed_time < 15.0:
#             msg.linear.x = 0.0
#             msg.angular.z = -0.5236  # Kecepatan rotasi (rad/s)
#             self.get_logger().info('Rotasi Kanan 90 Derajat')
#         elif elapsed_time < 21.0:
#             msg.linear.x = 0.5 # Kecepatan linear (m/s)
#             msg.angular.z = 0.0  
#             self.get_logger().info('Gerak Maju 6s')
#         elif elapsed_time < 24.0:
#             msg.linear.x = 0.0
#             msg.angular.z = -0.5236  # Kecepatan rotasi (rad/s)
#             self.get_logger().info('Rotasi Kanan 90 Derajat')
#         elif elapsed_time < 27.0:
#             msg.linear.x = 0.5 # Kecepatan linear (m/s)
#             msg.angular.z = 0.0  
#             self.get_logger().info('Gerak Maju 3s')
#         elif elapsed_time < 30.0:
#             msg.linear.x = 0.0
#             msg.angular.z = -0.5236  # Kecepatan rotasi (rad/s)
#             self.get_logger().info('Rotasi Kanan 90 Derajat')
#         else:
#             msg.linear.x = 0.0
#             msg.angular.z = 0.0
#             self.get_logger().info('Berhenti.')
#             self.publisher_.publish(msg)
            
#             self.timer.cancel()
#             rclpy.shutdown()
#             return

#         self.publisher_.publish(msg)

# def main(args=None):
#     rclpy.init(args=args)
#     node = MoverNode()
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
from geometry_msgs.msg import Twist
import threading
import time

class ForwardKinematicsCLI(Node):
    def __init__(self):
        super().__init__('forward_kinematics_cli')
        
        # Parameter robot (sama dengan sebelumnya)
        self.wheel_radius = 0.03
        self.wheel_separation = 0.17
        
        # Publisher untuk kecepatan keseluruhan robot (Twist)
        self.publisher_ = self.create_publisher(Twist, '/cmd_vel', 10)
        
        self.get_logger().info('Forward kinematics aktif. Menunggu input CLI...')

        # Menjalankan thread terpisah untuk input CLI
        self.cli_thread = threading.Thread(target=self.input_loop)
        self.cli_thread.daemon = True
        self.cli_thread.start()

    def input_loop(self):
        while rclpy.ok():
            try:
                print("\n--- Input Roda (Forward Kinematics) ---")
                omega_l = float(input("Masukkan kec. roda kiri (omega_l) rad/s  : "))
                omega_r = float(input("Masukkan kec. roda kanan (omega_r) rad/s : "))
                t = float(input("Masukkan durasi gerak (t) detik           : "))
                
                # 1. Mulai bergerak sesuai input roda
                self.calculate_and_publish(omega_l, omega_r)
                self.get_logger().info(f'Mengeksekusi Twist selama {t} detik...')
                
                # 2. Tunggu selama durasi (t)
                time.sleep(t)
                
                # 3. Hentikan robot setelah waktu habis
                self.calculate_and_publish(0.0, 0.0)
                self.get_logger().info('Waktu habis. Robot berhenti.')
                
            except ValueError:
                print("Input tidak valid. Harap masukkan angka.")
            except EOFError:
                break

    def calculate_and_publish(self, omega_l, omega_r):
        R = self.wheel_radius
        L = self.wheel_separation

        # Perhitungan Forward Kinematics
        v = (R / 2.0) * (omega_r + omega_l)
        w = (R / L) * (omega_r - omega_l)

        # Membuat dan mengisi pesan Twist
        msg = Twist()
        msg.linear.x = float(v)
        msg.angular.z = float(w)

        # Publish nilai ke topic /cmd_vel
        self.publisher_.publish(msg)

        self.get_logger().info(
            f'Kalkulasi FK -> Linear (v): {v:.3f} m/s, Angular (w): {w:.3f} rad/s'
        )

def main(args=None):
    rclpy.init(args=args)
    node = ForwardKinematicsCLI()
    
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