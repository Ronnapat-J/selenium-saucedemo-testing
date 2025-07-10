from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import json

# โหลด Configuration
with open("config.json", "r") as file:
    config = json.load(file)

USERNAME = config["username"]
PASSWORD = config["password"]
KEYWORDS = config["keywords"]

# สร้างไฟล์บันทึก Log
log_file = open("test_log.txt", "w", encoding="utf-8")
test_result = {"test_steps": []}

def log_message(message):
    print(message)
    with open("test_log.txt", "a", encoding="utf-8") as log_file:
        log_file.write(message + "\n")  # บันทึกลงไฟล์
    test_result["test_steps"].append(message)  # เก็บข้อมูลไว้ใน JSON

# เริ่มต้น WebDriver
driver = webdriver.Chrome()

# 1️⃣ เข้าเว็บ Saucedemo
driver.get("https://www.saucedemo.com/")
time.sleep(2)
log_message("🔗 เปิดหน้าเว็บ Saucedemo")

# 2️⃣ Login
driver.find_element(By.ID, "user-name").send_keys(USERNAME)
driver.find_element(By.ID, "password").send_keys(PASSWORD)
driver.find_element(By.ID, "login-button").click()
time.sleep(3)
log_message("🔑 Login สำเร็จ")

# 3️⃣ ค้นหาสินค้า & เพิ่มลงตะกร้า
for keyword in KEYWORDS:
    try:
        product_element = driver.find_element(By.XPATH, f"//div[text()='{keyword}']")
        add_to_cart_button = product_element.find_element(By.XPATH, "./ancestor::div[@class='inventory_item']//button")
        add_to_cart_button.click()
        log_message(f"✅ เพิ่ม {keyword} ลงตะกร้าเรียบร้อย")
        time.sleep(1)
    except Exception as e:
        log_message(f"❌ ไม่พบสินค้า: {keyword} - Error: {str(e)}")

# 4️⃣ ไปที่ตะกร้า
driver.find_element(By.CLASS_NAME, "shopping_cart_link").click()
time.sleep(2)
log_message("🛒 เปิดหน้าตะกร้าสินค้า")

# 5️⃣ คืนสินค้า (ลบ Backpack ออกจากตะกร้า)
try:
    backpack_remove_button = driver.find_element(By.XPATH, "//div[text()='Sauce Labs Backpack']/ancestor::div[@class='cart_item']//button")
    backpack_remove_button.click()
    log_message("✅ ลบ Backpack ออกจากตะกร้าเรียบร้อย")
    time.sleep(1)
except Exception as e:
    log_message(f"❌ ไม่พบ Backpack ในตะกร้า - Error: {str(e)}")

# 6️⃣ Checkout
driver.find_element(By.ID, "checkout").click()
time.sleep(2)
log_message("💳 ดำเนินการ Checkout")

# 7️⃣ กรอกข้อมูลลูกค้า
driver.find_element(By.ID, "first-name").send_keys("Ronnapat")
driver.find_element(By.ID, "last-name").send_keys("Jitsom")
driver.find_element(By.ID, "postal-code").send_keys("10230")
driver.find_element(By.ID, "continue").click()
time.sleep(2)
log_message("📝 กรอกข้อมูลลูกค้า")

# 8️⃣ ตรวจสอบราคารวม + ภาษี 8%
subtotal = float(driver.find_element(By.CLASS_NAME, "summary_subtotal_label").text.split("$")[1])
tax = round(subtotal * 0.08, 2)
total_price = float(driver.find_element(By.CLASS_NAME, "summary_total_label").text.split("$")[1])

log_message(f"💰 ราคาสินค้า: ${subtotal}")
log_message(f"💰 ภาษี 8%: ${tax}")
log_message(f"💰 ราคารวม (รวมภาษี): ${total_price}")

expected_total = round(subtotal + tax, 2)
if expected_total == total_price:
    log_message("✅ ราคาถูกต้อง")
else:
    log_message("❌ ราคาผิดพลาด")

# 9️⃣ ยืนยันการสั่งซื้อ
driver.find_element(By.ID, "finish").click()
time.sleep(2)
log_message("🛍️ ยืนยันการสั่งซื้อ")

# 🔟 ตรวจสอบผลลัพธ์
success_message = driver.find_element(By.CLASS_NAME, "complete-header").text
if "THANK YOU FOR YOUR ORDER" in success_message.upper():
    log_message("🎉 การสั่งซื้อสำเร็จ!")
    test_result["result"] = "Success"
else:
    log_message("❌ เกิดข้อผิดพลาดในการสั่งซื้อ")
    test_result["result"] = "Failed"

# ปิด Browser
driver.quit()

# 🔹 ปิดไฟล์ Log
log_file.close()

# 🔹 บันทึกผลลัพธ์ลง JSON
with open("test_result.json", "w", encoding="utf-8") as json_file:
    json.dump(test_result, json_file, indent=4, ensure_ascii=False)

log_message("📁 บันทึก Log และ Test Result สำเร็จ")
