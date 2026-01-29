document.addEventListener("DOMContentLoaded", () => {
  // --- Utility: get CSRF token from cookie ---
  const getCookie = (name) => {
    const cookies = document.cookie.split(";");
    for (let cookie of cookies) {
      cookie = cookie.trim();
      if (cookie.startsWith(name + "=")) {
        return decodeURIComponent(cookie.substring(name.length + 1));
      }
    }
    return "";
  };

  // --- Like/Dislike buttons ---
  document.querySelectorAll(".like-btn, .dislike-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      if (btn.disabled) return;
      btn.disabled = true;

      const comment = btn.closest(".comment");
      const likeBtn = comment.querySelector(".like-btn");
      const dislikeBtn = comment.querySelector(".dislike-btn");
      const url = btn.dataset.url;

      const isLikeClicked = btn.classList.contains("like-btn");
      const activeLike = likeBtn.classList.contains("active");
      const activeDislike = dislikeBtn.classList.contains("active");

      if ((isLikeClicked && activeLike) || (!isLikeClicked && activeDislike)) {
        btn.disabled = false;
        return;
      }

      fetch(url, {
        method: "POST",
        headers: { "X-CSRFToken": getCookie("csrftoken") },
        credentials: "same-origin",
      })
        .then((res) => res.json())
        .then((data) => {
          comment.querySelector(".like-count").textContent = data.likes;
          comment.querySelector(".dislike-count").textContent = data.dislikes;

          likeBtn.classList.toggle("active", isLikeClicked);
          dislikeBtn.classList.toggle("active", !isLikeClicked);
        })
        .catch(console.error)
        .finally(() => {
          btn.disabled = false;
        });
    });
  });

  // --- Star rating ---
  document.querySelectorAll(".star-form").forEach((form) => {
    const stars = form.querySelectorAll(".star-btn");
    const msg = form.querySelector(".rating-msg");
    const url = form.dataset.url;

    stars.forEach((starBtn) => {
      starBtn.addEventListener("click", () => {
        const rating = parseInt(starBtn.value);

        // Send rating to server
        const formData = new FormData();
        formData.append("rating", rating);

        fetch(url, {
          method: "POST",
          headers: { "X-CSRFToken": getCookie("csrftoken") },
          body: formData,
          credentials: "same-origin",
        })
          .then((res) => res.json())
          .then((data) => {
            if (data.error) return alert(data.error);

            // Highlight stars up to selected rating
            stars.forEach((s) => {
              if (parseInt(s.value) <= data.rating) {
                s.classList.add("selected");
              } else {
                s.classList.remove("selected");
              }
            });

            // Update message
            if (msg) {
              msg.textContent = `Your rating: ${data.rating} ★ (click to change)`;
            }

            // Update average rating display
            const avgElem = document.querySelector(".rating-box p");
            if (avgElem && data.average_rating !== undefined && data.rating_count !== undefined) {
              avgElem.innerHTML = `⭐ Average: ${data.average_rating.toFixed(1)} (${data.rating_count} rating${data.rating_count !== 1 ? "s" : ""})`;
            }
          })
          .catch(console.error);
      });
    });
  });
});
