const scrollContainer = document.getElementById("carroussel");

scrollContainer.addEventListener("wheel", (evt) => {
    evt.preventDefault();
    scrollContainer.scrollLeft += evt.deltaY * 3;
});