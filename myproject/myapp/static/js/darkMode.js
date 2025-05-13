// ฟังก์ชันสำหรับสลับระหว่างโหมดมืดและโหมดสว่าง
function setupDarkMode() {
  // ตรวจสอบค่าที่บันทึกไว้ใน localStorage หรือการตั้งค่าระบบ
  if (localStorage.getItem('color-theme') === 'dark' || 
     (!('color-theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
    document.documentElement.classList.add('dark');
  } else {
    document.documentElement.classList.remove('dark');
  }
  
  // รับปุ่มสลับโหมด
  const themeToggle = document.getElementById('theme-toggle');
  
  if (themeToggle) {
    themeToggle.addEventListener('click', function() {
      // สลับคลาส dark ใน document.documentElement (HTML tag)
      document.documentElement.classList.toggle('dark');
      
      // บันทึกค่าลงใน localStorage
      if (document.documentElement.classList.contains('dark')) {
        localStorage.setItem('color-theme', 'dark');
      } else {
        localStorage.setItem('color-theme', 'light');
      }
    });
  }
}

// รันฟังก์ชันเมื่อเว็บโหลดเสร็จ
document.addEventListener('DOMContentLoaded', setupDarkMode);