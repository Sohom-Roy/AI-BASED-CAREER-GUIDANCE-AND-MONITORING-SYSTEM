#!/usr/bin/env python3
"""
MQTT Test Script for AI-Enhanced Career Guidance System
This script simulates ESP32 data for testing the monitoring functionality.
"""

import paho.mqtt.client as mqtt
import time
import random
import json

# MQTT Configuration
BROKER = 'localhost'
PORT = 1883
USER_ID = 1  # Change this to test with different users

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Connected to MQTT Broker!")
    else:
        print(f"❌ Failed to connect, return code {rc}")

def on_disconnect(client, userdata, rc):
    print("🔌 Disconnected from MQTT Broker")

def simulate_focus_data():
    """Simulate ESP32 focus monitoring data"""
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    
    try:
        client.connect(BROKER, PORT, 60)
        client.loop_start()
        
        print(f"🎯 Simulating focus data for user {USER_ID}")
        print("Press Ctrl+C to stop...")
        
        while True:
            # Simulate realistic focus patterns
            # More likely to be focused during "study hours" (9 AM - 5 PM)
            current_hour = time.localtime().tm_hour
            if 9 <= current_hour <= 17:
                focus_probability = 0.7  # 70% chance of being focused
            else:
                focus_probability = 0.3  # 30% chance of being focused
            
            is_focused = random.random() < focus_probability
            status = "true" if is_focused else "false"
            
            # Publish focus status
            topic = f"monitor/{USER_ID}/focus"
            client.publish(topic, status)
            
            # Add some metadata
            metadata = {
                "timestamp": time.time(),
                "confidence": random.uniform(0.7, 0.95),
                "session_duration": random.randint(5, 60)
            }
            
            metadata_topic = f"monitor/{USER_ID}/metadata"
            client.publish(metadata_topic, json.dumps(metadata))
            
            print(f"📊 Published: {topic} -> {status} (Confidence: {metadata['confidence']:.2f})")
            
            # Wait 10-30 seconds between updates
            time.sleep(random.randint(10, 30))
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping simulation...")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        client.loop_stop()
        client.disconnect()

def test_single_message():
    """Send a single test message"""
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    
    try:
        client.connect(BROKER, PORT, 60)
        client.loop_start()
        
        # Send test messages
        topic = f"monitor/{USER_ID}/focus"
        
        print("📤 Sending test messages...")
        client.publish(topic, "true")
        time.sleep(2)
        client.publish(topic, "false")
        time.sleep(2)
        client.publish(topic, "true")
        
        print("✅ Test messages sent!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        client.loop_stop()
        client.disconnect()

def main():
    print("🧪 MQTT Test Script for Career Guidance System")
    print("=" * 50)
    print(f"Broker: {BROKER}:{PORT}")
    print(f"User ID: {USER_ID}")
    print()
    
    print("Choose test mode:")
    print("1. Single test message")
    print("2. Continuous simulation")
    print("3. Exit")
    
    choice = input("Enter choice (1-3): ").strip()
    
    if choice == "1":
        test_single_message()
    elif choice == "2":
        simulate_focus_data()
    elif choice == "3":
        print("👋 Goodbye!")
    else:
        print("❌ Invalid choice!")

if __name__ == "__main__":
    main()
