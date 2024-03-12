// const elem = document.querySelectorAll(".card-holder");

// elem.forEach(element => {
//     element.addEventListener("wheel", (evt) => {
//         evt.preventDefault();
//         element.scrollLeft += evt.deltaY * 3;
//     });
// });

const cardHolders = document.querySelectorAll(".card-holder");

cardHolders.forEach(cardHolder => {
  cardHolder.addEventListener("mousedown", (event) => startDrag(event, cardHolder));
  cardHolder.addEventListener("mousemove", (event) => drag(event, cardHolder));
  document.addEventListener("mouseup", stopDrag);
});

let isDragging = false;
let startX = 0;

function startDrag(event, cardHolder) {
  isDragging = true;
  startX = event.clientX - cardHolder.scrollLeft;
}

function drag(event, cardHolder) {
  if (!isDragging) return;
  cardHolder.scrollLeft = startX - event.clientX;
}

function stopDrag() {
  isDragging = false;
}
