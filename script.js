document.getElementById("fileUpload").addEventListener("change", function(event) {
    const file = event.target.files[0];
    const previewContainer = document.getElementById("image-preview");

    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            previewContainer.innerHTML = `<img src="${e.target.result}" alt="Uploaded Flowchart" class="preview-image">`;
        };
        reader.readAsDataURL(file);
    }
});
