class MediaHandler {
  // 图片懒加载（对应功能3.1.2）
  initLazyLoad() {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const img = entry.target;
          img.src = img.dataset.src;
          observer.unobserve(img);
        }
      });
    });

    document.querySelectorAll('[data-lazy]').forEach(img => {
      observer.observe(img);
    });
  }

  // 视频预览初始化（对应功能3.2.2）
  initVideoPlayers() {
    document.querySelectorAll('.video-thumbnail').forEach(video => {
      video.addEventListener('click', () => {
        const videoContainer = video.closest('.media-container');
        videoContainer.innerHTML = `
          <video controls width="100%">
            <source src="${video.dataset.src}" type="video/mp4">
          </video>
        `;
      });
    });
  }
}