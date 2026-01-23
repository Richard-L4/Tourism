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

  document.querySelectorAll(".like-btn, .dislike-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      if (btn.disabled) return; // ignore if already in progress
      btn.disabled = true;

      const comment = btn.closest(".comment");
      const likeBtn = comment.querySelector(".like-btn");
      const dislikeBtn = comment.querySelector(".dislike-btn");
      const url = btn.dataset.url;

      // Determine current state
      const isLikeClicked = btn.classList.contains("like-btn");
      const activeLike = likeBtn.classList.contains("active");
      const activeDislike = dislikeBtn.classList.contains("active");

      // Only allow switching if necessary
      if ((isLikeClicked && activeLike) || (!isLikeClicked && activeDislike)) {
        btn.disabled = false; // do nothing if user clicks the same active button
        return;
      }

      fetch(url, {
        method: "POST",
        headers: { "X-CSRFToken": getCookie("csrftoken") },
        credentials: "same-origin",
      })
        .then((res) => res.json())
        .then((data) => {
          // Update counts
          comment.querySelector(".like-count").textContent = data.likes;
          comment.querySelector(".dislike-count").textContent = data.dislikes;

          // Update active states
          likeBtn.classList.toggle("active", isLikeClicked);
          dislikeBtn.classList.toggle("active", !isLikeClicked);
        })
        .catch(console.error)
        .finally(() => {
          btn.disabled = false;
        });
    });
  });
});