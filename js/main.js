document.getElementById("year").textContent = new Date().getFullYear();

const navToggle = document.getElementById("navToggle");
const navLinks = document.getElementById("navLinks");

navToggle.addEventListener("click", () => {
  const isOpen = navLinks.classList.toggle("open");
  navToggle.setAttribute("aria-expanded", isOpen);
});

navLinks.querySelectorAll("a").forEach((link) => {
  link.addEventListener("click", () => {
    navLinks.classList.remove("open");
    navToggle.setAttribute("aria-expanded", "false");
  });
});

const contactForm = document.getElementById("contactForm");
const formStatus = document.getElementById("formStatus");

contactForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  formStatus.textContent = "Sending...";

  try {
    const response = await fetch(contactForm.action, {
      method: "POST",
      body: new FormData(contactForm),
      headers: { Accept: "application/json" },
    });

    if (response.ok) {
      formStatus.textContent = "Thanks! Your message has been sent.";
      contactForm.reset();
    } else {
      formStatus.textContent = "Something went wrong. Please email coachkatysavage@gmail.com directly.";
    }
  } catch (err) {
    formStatus.textContent = "Something went wrong. Please email coachkatysavage@gmail.com directly.";
  }
});
