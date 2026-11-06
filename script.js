document.addEventListener("DOMContentLoaded", () => {
  const gallery = document.getElementById("gallery");
  const sizeSlider = document.getElementById("size-slider");

  // 1. Dynamic Resizing Control
  sizeSlider.addEventListener("input", (e) => {
    // Dynamically set the CSS Variable '--img-size'
    document.documentElement.style.setProperty("--img-size", `${e.target.value}px`);
  });

  // 2. Automatically load images from assets folder
  loadGalleryImages();

  async function loadGalleryImages() {
    try {
      // Fetch the list of image filenames from assets/assets.json
      const response = await fetch("assets/assets.json");
      if (!response.ok) throw new Error("Could not find assets/assets.json file.");
      
      const imageFiles = await response.json();

      // Clear gallery
      gallery.innerHTML = "";

      // Append images to gallery dynamically
      imageFiles.forEach((fileName) => {
        const itemDiv = document.createElement("div");
        itemDiv.className = "gallery-item";

        const img = document.createElement("img");
        img.src = `assets/${fileName}`;
        img.alt = fileName;
        img.loading = "lazy"; // Optimize for unlimited images

        itemDiv.appendChild(img);
        gallery.appendChild(itemDiv);
      });
    } catch (error) {
      console.error("Error loading images:", error);
      gallery.innerHTML = `<p style="color: #ff6b6b;">Error loading images. Please ensure 'assets/assets.json' exists.</p>`;
    }
  }
});