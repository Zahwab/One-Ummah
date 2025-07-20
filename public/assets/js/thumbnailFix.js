// assets/js/thumbnailFix.js
document.addEventListener('DOMContentLoaded', () => {
  // wait for the real openModal
  if (typeof window.openModal !== 'function') return;

  // find (or create) the <img> in your modal
  let thumbEl = document.getElementById('pdfThumb');
  if (!thumbEl) {
    const nameEl = document.getElementById('pdfName');
    const modalContent = document.querySelector('#pdfModal .modal-content');
    thumbEl = document.createElement('img');
    thumbEl.id = 'pdfThumb';
    thumbEl.className = 'thumbnail-preview';
    thumbEl.alt = 'PDF Thumbnail';
    if (modalContent && nameEl) {
      modalContent.insertBefore(thumbEl, nameEl);
    }
  }
  if (!thumbEl) return;

  // wrap the original openModal
  const _openModal = window.openModal;
  window.openModal = function(book) {
    // book.thumb might be just "foo.webp" or "thumbnails/foo.webp"
    let url = book.thumb;
    // if it’s only a filename, prepend the folder
    if (!url.includes('/')) {
      url = 'thumbnails/' + url;
    }
    // drop any stray "public/" prefix (since you're already in /public)
    url = url.replace(/^public\//, '');

    thumbEl.src = url;
    return _openModal(book);
  };
});