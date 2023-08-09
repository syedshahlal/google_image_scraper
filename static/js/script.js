/* script.js */
const submitButton = document.querySelector("input[type='submit']");

submitButton.addEventListener("mouseenter", () => {
    submitButton.style.backgroundColor = "#0056B3";
    submitButton.style.color = "#FFFFFF";
});

submitButton.addEventListener("mouseleave", () => {
    submitButton.style.backgroundColor = "#007BFF";
    submitButton.style.color = "black";
});

submitButton.addEventListener("click", () => {
    submitButton.style.backgroundColor = "#0056B3";
    submitButton.style.transform = "scale(0.98)";
    setTimeout(() => {
        submitButton.style.transform = "scale(1)";
    }, 200);
});
