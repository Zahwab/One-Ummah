// assets/js/thumbnailModal.js

document.addEventListener('DOMContentLoaded', () => {
  // Wait until your original openModal(book) exists
  if (typeof window.openModal !== 'function') {
    console.warn('thumbnailModal.js: openModal() not found. Make sure this script loads after your main script.');
    return;
  }

  // Grab a reference to the thumbnail <img> in the modal
  const thumbEl = document.getElementById('pdfThumb');
  if (!thumbEl) {
    console.warn('thumbnailModal.js: #pdfThumb element not found in DOM.');
  }

  // Keep the original openModal around
  const _openModal = window.openModal;

  // Override it
  window.openModal = function(book) {
    // 1) Inject the thumbnail URL
    if (thumbEl && book.thumb) {
      // Since knowledge.html lives in /public, and your thumbnails are in /public/thumbnails
      thumbEl.src = `thumbnails/${book.thumb}`;
    }

    // 2) Call the original openModal to do everything else (name, size, links, show modal)
    return _openModal(book);
  };
});