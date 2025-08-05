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

// Mobile Menu Functionality

// ...rest of your existing script.js code...

// Tab functionality with URL support
document.addEventListener("DOMContentLoaded", function () {
  const tabButtons = document.querySelectorAll(".tab-btn");
  const tabContents = document.querySelectorAll(".tab-content");

  // Get active tab from URL or default to overview
  const urlParams = new URLSearchParams(window.location.search);
  const activeTab = urlParams.get("tab") || "users";

  // Show active tab
  showTab(activeTab);

  tabButtons.forEach((button) => {
    button.addEventListener("click", () => {
      const tab = button.getAttribute("data-tab");
      showTab(tab);

      // Update URL without reload
      const newUrl = new URL(window.location);
      newUrl.searchParams.set("tab", tab);
      window.history.pushState({}, "", newUrl);
    });
  });

  function showTab(tabName) {
    // Remove active class from all buttons and contents
    tabButtons.forEach((btn) => btn.classList.remove("active"));
    tabContents.forEach((content) => content.classList.remove("active"));

    // Add active class to selected button and content
    const activeButton = document.querySelector(`[data-tab="${tabName}"]`);
    const activeContent = document.getElementById(`${tabName}-tab`);

    if (activeButton && activeContent) {
      activeButton.classList.add("active");
      activeContent.classList.add("active");
    }
  }

  // Search functionality for users table
  const searchInput = document.getElementById("userSearch");
  if (searchInput) {
    searchInput.addEventListener("input", function () {
      const searchTerm = this.value.toLowerCase();
      const userRows = document.querySelectorAll(".user-row");

      userRows.forEach((row) => {
        const userName = row.querySelector("strong").textContent.toLowerCase();
        const userEmail = row.cells[1].textContent.toLowerCase();

        if (userName.includes(searchTerm) || userEmail.includes(searchTerm)) {
          row.style.display = "";
        } else {
          row.style.display = "none";
        }
      });
    });
  }
});

// Handle profile picture fallback
document.addEventListener("DOMContentLoaded", function () {
  const profilePics = document.querySelectorAll("img[data-fallback-src]");
  profilePics.forEach((img) => {
    img.addEventListener("error", function () {
      this.src = this.getAttribute("data-fallback-src");
    });
  });

  // Handle session error redirect
  const sessionError = document.getElementById("session-error");
  if (sessionError) {
    const loginUrlScript = document.getElementById("login-url");
    if (loginUrlScript) {
      const loginUrl = loginUrlScript.textContent;
      setTimeout(function () {
        window.location.href = loginUrl;
      }, 3000);
    }
  }
});

/* filepath: c:\Users\X\alumni_site_fixed_v2\static\script.js */
// Add this to your existing script.js
document.addEventListener("DOMContentLoaded", function () {
  const mobileToggle = document.querySelector(".mobile-menu-toggle");
  const navLinks = document.querySelector(".nav-links");
  const body = document.body;

  if (mobileToggle && navLinks) {
    mobileToggle.addEventListener("click", function () {
      this.classList.toggle("active");
      navLinks.classList.toggle("mobile-active");
      body.style.overflow = navLinks.classList.contains("mobile-active")
        ? "hidden"
        : "";
    });

    // Close menu when clicking on a link
    navLinks.querySelectorAll("a").forEach((link) => {
      link.addEventListener("click", () => {
        mobileToggle.classList.remove("active");
        navLinks.classList.remove("mobile-active");
        body.style.overflow = "";
      });
    });

    // Close menu when clicking outside
    document.addEventListener("click", function (e) {
      if (!mobileToggle.contains(e.target) && !navLinks.contains(e.target)) {
        mobileToggle.classList.remove("active");
        navLinks.classList.remove("mobile-active");
        body.style.overflow = "";
      }
    });
  }
});
