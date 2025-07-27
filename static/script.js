// Dark mode functionality
function toggleDarkMode() {
  const body = document.body;
  const modeIcon = document.getElementById("mode-icon");
  const modeText = document.getElementById("mode-text");

  body.classList.toggle("dark-mode");

  if (body.classList.contains("dark-mode")) {
    modeIcon.textContent = "☀️";
    modeText.textContent = "Light";
    localStorage.setItem("darkMode", "enabled");
  } else {
    modeIcon.textContent = "🌙";
    modeText.textContent = "Dark";
    localStorage.setItem("darkMode", "disabled");
  }
}

// Check for saved dark mode preference or default to light mode
document.addEventListener("DOMContentLoaded", () => {
  const darkMode = localStorage.getItem("darkMode");
  const modeIcon = document.getElementById("mode-icon");
  const modeText = document.getElementById("mode-text");

  if (darkMode === "enabled") {
    document.body.classList.add("dark-mode");
    modeIcon.textContent = "☀️";
    modeText.textContent = "Light";
  }
});

// Smooth scrolling for navigation links
document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
  anchor.addEventListener("click", function (e) {
    e.preventDefault();
    const target = document.querySelector(this.getAttribute("href"));
    if (target) {
      target.scrollIntoView({
        behavior: "smooth",
        block: "start",
      });
    }
  });
});

// Navbar background change on scroll
window.addEventListener("scroll", () => {
  const nav = document.querySelector("nav");
  const isDarkMode = document.body.classList.contains("dark-mode");

  if (window.scrollY > 100) {
    if (isDarkMode) {
      nav.style.background = "rgba(26, 26, 26, 0.98)";
    } else {
      nav.style.background = "rgba(255, 255, 255, 0.98)";
    }
    nav.style.boxShadow = "0 2px 20px rgba(0, 116, 217, 0.15)";
  } else {
    if (isDarkMode) {
      nav.style.background = "rgba(26, 26, 26, 0.95)";
    } else {
      nav.style.background = "rgba(255, 255, 255, 0.95)";
    }
    nav.style.boxShadow = "none";
  }
});

// Scroll animations
const observerOptions = {
  threshold: 0.1,
  rootMargin: "0px 0px -50px 0px",
};

const observer = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    if (entry.isIntersecting) {
      entry.target.classList.add("animated");
    }
  });
}, observerOptions);

document.querySelectorAll(".scroll-animate").forEach((el) => {
  observer.observe(el);
});

// Counter animation for statistics
const animateCounters = () => {
  const counters = document.querySelectorAll(".stat-item h3");
  counters.forEach((counter) => {
    const target = parseInt(counter.innerText.replace(/[^\d]/g, ""));
    const increment = target / 100;
    let current = 0;

    const updateCounter = () => {
      if (current < target) {
        current += increment;
        if (counter.innerText.includes("+")) {
          counter.innerText = Math.ceil(current).toLocaleString() + "+";
        } else if (counter.innerText.includes("%")) {
          counter.innerText = Math.ceil(current) + "%";
        } else if (counter.innerText.includes("₦")) {
          counter.innerText = "₦" + Math.ceil(current) + "M+";
        } else {
          counter.innerText = Math.ceil(current).toLocaleString();
        }
        setTimeout(updateCounter, 50);
      }
    };
    updateCounter();
  });
};

// Trigger counter animation when stats section is visible
const statsObserver = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    if (entry.isIntersecting) {
      animateCounters();
      statsObserver.unobserve(entry.target);
    }
  });
});

const statsSection = document.querySelector(".stats");
if (statsSection) {
  statsObserver.observe(statsSection);
}

// Tab switching
function showTab(tabName) {
  document
    .querySelectorAll(".tab-content")
    .forEach((tc) => tc.classList.remove("active"));
  document
    .querySelectorAll(".tab-btn")
    .forEach((btn) => btn.classList.remove("active"));
  document.getElementById(tabName + "-tab").classList.add("active");
  document
    .querySelector(`.tab-btn[data-tab="${tabName}"]`)
    .classList.add("active");
}

// Search filter
document.addEventListener("DOMContentLoaded", () => {
  const search = document.getElementById("userSearch");
  if (search) {
    search.addEventListener("input", (e) => {
      const term = e.target.value.toLowerCase();
      document.querySelectorAll(".user-row").forEach((row) => {
        row.style.display = row.textContent.toLowerCase().includes(term)
          ? ""
          : "none";
      });
    });
  }

  // Form loading state
  document.querySelectorAll("form").forEach((form) => {
    form.addEventListener("submit", () => {
      const btn = form.querySelector('button[type="submit"]');
      if (btn) {
        const txt = btn.innerHTML;
        btn.disabled = true;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing…';
        setTimeout(() => {
          btn.disabled = false;
          btn.innerHTML = txt;
        }, 3000);
      }
    });
  });
});

function toggleStateDropdown() {
  const country = document.getElementById("country");
  const stateWrapper = document.getElementById("state-wrapper");
  const citySelect = document.getElementById("city");

  // Only proceed if ALL required elements exist
  if (!country || !stateWrapper || !citySelect) {
    // Silently return instead of showing console warning on every page
    return;
  }

  if (country.value === "Nigeria") {
    stateWrapper.style.display = "block";
    citySelect.required = true;
  } else {
    stateWrapper.style.display = "none";
    citySelect.required = false;
  }
}

// Only attach the event listener if the country select exists
document.addEventListener("DOMContentLoaded", function () {
  const countrySelect = document.getElementById("country");
  if (countrySelect) {
    countrySelect.addEventListener("change", toggleStateDropdown);
    toggleStateDropdown(); // Run once on page load
  }
});

document.addEventListener("DOMContentLoaded", function () {
  const tabButtons = document.querySelectorAll(".tab-btn");
  const tabContents = document.querySelectorAll(".tab-content");

  tabButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      const target = btn.getAttribute("data-tab");

      // Remove active class from all buttons and contents
      tabButtons.forEach((b) => b.classList.remove("active"));
      tabContents.forEach((tc) => tc.classList.remove("active"));

      // Activate clicked button and corresponding content
      btn.classList.add("active");
      document.getElementById(`${target}-tab`).classList.add("active");
    });
  });
});

// Auto-hide flash messages after 5 seconds
document.addEventListener("DOMContentLoaded", function () {
  const alerts = document.querySelectorAll(".alert.auto-hide");
  alerts.forEach(function (alert, index) {
    setTimeout(function () {
      if (alert && alert.parentElement) {
        alert.style.animation = "fadeOut 0.5s ease-in forwards";
        setTimeout(function () {
          alert.style.display = "none";
        }, 500);
      }
    }, 5000 + index * 100); // Stagger the hiding if multiple alerts
  });
});

// Enhanced Mobile Menu Functionality - Add this to your script.js

document.addEventListener("DOMContentLoaded", function () {
  // Mobile menu toggle functionality - Enhanced
  const mobileToggle = document.getElementById("mobile-toggle");
  const navLinks = document.getElementById("nav-links");
  const body = document.body;

  if (mobileToggle && navLinks) {
    // Toggle mobile menu function
    function toggleMobileMenu() {
      const isActive = navLinks.classList.contains("mobile-active");

      console.log("Toggle clicked, current state:", isActive); // Debug log

      if (isActive) {
        // Close menu
        navLinks.classList.remove("mobile-active");
        mobileToggle.classList.remove("active");
        body.classList.remove("menu-open");
        console.log("Menu closed"); // Debug log
      } else {
        // Open menu
        navLinks.classList.add("mobile-active");
        mobileToggle.classList.add("active");
        body.classList.add("menu-open");
        console.log("Menu opened"); // Debug log
      }
    }

    // Event listeners
    mobileToggle.addEventListener("click", function (e) {
      e.preventDefault();
      e.stopPropagation();
      toggleMobileMenu();
    });

    // Close menu when clicking on navigation links
    document.querySelectorAll(".nav-links a").forEach((link) => {
      link.addEventListener("click", () => {
        navLinks.classList.remove("mobile-active");
        mobileToggle.classList.remove("active");
        body.classList.remove("menu-open");
        console.log("Menu closed via link click"); // Debug log
      });
    });

    // Close menu when clicking outside of it
    document.addEventListener("click", function (e) {
      if (
        !navLinks.contains(e.target) &&
        !mobileToggle.contains(e.target) &&
        navLinks.classList.contains("mobile-active")
      ) {
        navLinks.classList.remove("mobile-active");
        mobileToggle.classList.remove("active");
        body.classList.remove("menu-open");
        console.log("Menu closed via outside click"); // Debug log
      }
    });

    // Handle escape key to close menu
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && navLinks.classList.contains("mobile-active")) {
        navLinks.classList.remove("mobile-active");
        mobileToggle.classList.remove("active");
        body.classList.remove("menu-open");
        console.log("Menu closed via escape key"); // Debug log
      }
    });

    // Close menu on window resize if it gets too wide
    window.addEventListener("resize", function () {
      if (
        window.innerWidth > 768 &&
        navLinks.classList.contains("mobile-active")
      ) {
        navLinks.classList.remove("mobile-active");
        mobileToggle.classList.remove("active");
        body.classList.remove("menu-open");
        console.log("Menu closed via resize"); // Debug log
      }
    });
  } else {
    console.error("Mobile toggle or nav links not found"); // Debug log
  }
});
