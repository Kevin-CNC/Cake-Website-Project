document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("reviewForm");
    const reviewsSection = document.querySelector(".reviews");
  
    form.addEventListener("submit", function (e) {
      e.preventDefault();
  
      const name = document.getElementById("name").value.trim();
      const reviewText = document.getElementById("review").value.trim();
  
      if (name && reviewText) {
        const newReview = document.createElement("article");
        newReview.classList.add("review");
  
        const nameHeading = document.createElement("h3");
        nameHeading.textContent = name;
  
        const reviewPara = document.createElement("p");
        reviewPara.textContent = reviewText;
  
        newReview.appendChild(nameHeading);
        newReview.appendChild(reviewPara);
  
        // add new review above the form
        reviewsSection.appendChild(newReview);
  
        // clear the form
        form.reset();
      }
    });
  });
  