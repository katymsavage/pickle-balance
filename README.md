# Pickle Balance

Website for Pickle Balance — strength and balance coaching for pickleball players who are new to athleticism. Hosted on GitHub Pages at [picklebalance.co](https://picklebalance.co).

## Structure

- `index.html` — single-page site (Story, Method, Who It's For, Classes, Contact)
- `css/style.css` — styling
- `js/main.js` — nav toggle + contact form submission
- `CNAME` — custom domain config for GitHub Pages

## Contact form

The contact form posts to Formspree. Before it works, replace `YOUR_FORM_ID` in the form `action` in `index.html` with a real Formspree form ID:

1. Sign up free at [formspree.io](https://formspree.io) with the email you want submissions sent to.
2. Create a new form, copy its endpoint (`https://formspree.io/f/xxxxxxx`).
3. Paste it into the `action` attribute of `#contactForm` in `index.html`.

## Local preview

Just open `index.html` in a browser — no build step required.
