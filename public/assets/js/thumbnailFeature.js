// assets/js/thumbnailFeature.js
document.addEventListener('DOMContentLoaded', () => {
  // 1) Locate the modal-content container
  const modalContent = document.querySelector('#pdfModal .modal-content');
  if (!modalContent) return console.warn('thumbnailFeature: modal-content not found');

  // 2) Ensure <img id="pdfThumb"> exists
  let thumbEl = document.getElementById('pdfThumb');
  const nameEl  = document.getElementById('pdfName');
  if (!thumbEl && nameEl) {
    thumbEl = document.createElement('img');
    thumbEl.id    = 'pdfThumb';
    thumbEl.alt   = 'PDF Thumbnail';
    thumbEl.className = 'thumbnail-preview';
    thumbEl.src   = '';               // placeholder
    // insert it immediately before the Name paragraph
    modalContent.insertBefore(thumbEl, nameEl);
  }

  if (!thumbEl) return console.warn('thumbnailFeature: could not create/find thumbEl');

  // 3) Patch openModal(book)
  if (typeof window.openModal !== 'function') {
    return console.warn('thumbnailFeature: openModal() not found');
  }
  const _openModal = window.openModal;
  window.openModal = function(book) {
    // -- inject thumbnail (relative to public/knowledge.html)
    thumbEl.src = `thumbnails/${book.thumb}`;
    // -- call the original to fill name/size/links & show modal
    return _openModal(book);
  };
});