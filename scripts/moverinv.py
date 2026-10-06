#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64
import threading
import time  # Tambahkan modul time

class InverseKinematicsCLI(Node):
    def __init__(self):
        super().__init__('inverse_kinematics_cli')
        
        # Parameter robot berdasarkan referensi gambar
        self.wheel_radius = 0.03
        self.wheel_separation = 0.17
        
        # Publisher untuk roda kiri dan kanan
        self.left_publisher = self.create_publisher(Float64, '/left_wheel/command', 10)
        self.right_publisher = self.create_publisher(Float64, '/right_wheel/command', 10)
        
        self.get_logger().info('Inverse kinematics aktif. Menunggu input CLI...')

        # Menjalankan thread terpisah untuk input CLI agar tidak memblokir rclpy.spin()
        self.cli_thread = threading.Thread(target=self.input_loop)
        self.cli_thread.daemon = True
        self.cli_thread.start()

    def input_loop(self):
        while rclpy.ok():
            try:
                print("\n--- Input Pergerakan ---")
                v = float(input("Masukkan kecepatan linear (v) m/s  : "))
                w = float(input("Masukkan kecepatan sudut (w) rad/s : "))
                t = float(input("Masukkan durasi gerak (t) detik    : "))
                
                # 1. Mulai bergerak sesuai input
                self.calculate_and_publish(v, w)
                self.get_logger().info(f'Robot akan bergerak selama {t} detik...')
                
                # 2. Tunggu selama durasi (t) yang ditentukan
                time.sleep(t)
                
                # 3. Hentikan robot setelah waktu habis (kirim kecepatan 0)
                self.calculate_and_publish(0.0, 0.0)
                self.get_logger().info('Waktu habis. Robot berhenti.')
                
            except ValueError:
                print("Input tidak valid. Harap masukkan angka.")
            except EOFError:
                break

    def calculate_and_publish(self, v, w):
        R = self.wheel_radius
        L = self.wheel_separation

        # Perhitungan Inverse Kinematics
        omega_l = (v - (w * L / 2.0)) / R
        omega_r = (v + (w * L / 2.0)) / R

        # Membuat dan mengisi pesan Float64
        msg_left = Float64()
        msg_left.data = omega_l
        
        msg_right = Float64()
        msg_right.data = omega_r

        # Publish nilai ke topic roda
        self.left_publisher.publish(msg_left)
        self.right_publisher.publish(msg_right)

        self.get_logger().info(f'Published -> Left Wheel: {omega_l:.2f} rad/s, Right Wheel: {omega_r:.2f} rad/s')

def main(args=None):
    rclpy.init(args=args)
    node = InverseKinematicsCLI()
    
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