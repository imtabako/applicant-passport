/* set date pickers' max value to `today' */
const bd_date = document.getElementById("birthday");
const rc_date = document.getElementById("receipt_date");
const today = new Date().toISOString().split("T")[0];
bd_date.max = today;
rc_date.max = today;

/* tweak for resizing textareas according to input */
const tx = document.getElementsByTagName("textarea");
for (let i = 0; i < tx.length; i++) {
    tx[i].setAttribute("style", "height:" + (tx[i].scrollHeight) + "px;overflow-y:hidden;");
    tx[i].addEventListener("input", OnInput, false);
}

function OnInput() {
    this.style.height = this.style['min-height'];
    this.style.height = (this.scrollHeight) + "px";
}

/* disable page refresh */
document.addEventListener('DOMContentLoaded', function () {
    document.getElementById('passport-form').addEventListener('submit', function (e) {
        e.preventDefault();

        var formData = new FormData(this);
        var xhr = new XMLHttpRequest();
        xhr.open('POST', '/postdata', true);
        xhr.onload = function () {
            if (xhr.status === 200) {
                console.log(xhr.response);
            }
        };
        xhr.send(formData);
    });
});

/* drag&drop photo */
const allowedExtensions = ['image/jpeg', 'image/jpg', 'image/png'];

const dropArea = document.getElementById('drop-area');
const inputFile = document.getElementById('file');
const imageView = document.getElementById('img-view');

inputFile.addEventListener('change', uploadImage);

function uploadImage() {
    let type = inputFile.files[0].type;
    if (allowedExtensions.indexOf(type) < 0) {
        return;
    }

    let imgLink = URL.createObjectURL(inputFile.files[0]);
    let image = new Image();
    image.src = imgLink;
    image.onload = function () {
        imageView.style.aspectRatio = (this.width / this.height).toString()
        if (this.width > this.height) {
            dropArea.style.minHeight = '0px';
        }
    }
    imageView.style.backgroundImage = `url(${imgLink})`;
    imageView.textContent = '';
    imageView.style.borderStyle = 'none';
}

dropArea.addEventListener('dragover', function (e) {
    e.preventDefault();
})
dropArea.addEventListener('drop', function (e) {
    e.preventDefault();
    inputFile.files = e.dataTransfer.files;
    uploadImage();
})