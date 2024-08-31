const surveyForm = document.querySelector("[multi-step-survey]");
const surveyPages = [...surveyForm.querySelectorAll("[data-step]")];
const genreButtons = document.querySelectorAll(".genre-btn");
const keywordInput = document.getElementById("keywords");
const descInput = document.getElementById("desc");

let curPage = surveyPages.findIndex(step => {
    return step.classList.contains("active")
})

console.log(curPage)

// set curPage if it is not set
if (curPage < 0) {
    curPage = 0;
    surveyPages[curPage].classList.add("active");
    displayCurrentPage();
}

// change survey page when user clicks next
surveyForm.addEventListener("click", event => {
    if (event.target.matches("[next-page]")) {
        curPage += 1;
        displayCurrentPage();
    } else if (event.target.matches("[prev-page]")) {
        curPage -= 1;
        displayCurrentPage();
    }
})

// set the curPage widget to active 
let displayCurrentPage = () => {
    surveyPages.forEach((step, index) => {
        console.log("display page")
        step.classList.toggle("active", index === curPage);
    })
}

// changes the color of the button when user toggles genre button
genreButtons.forEach(function(btn) {
    btn.addEventListener("click", function (event) {
        event.preventDefault();
        if (this.style.background === "rgb(212, 242, 246)") {
            console.log("light mint")
            // set color to mint
            console.log(this.style.background);
            this.style.background = "rgb(162, 227, 236)";
            console.log(this.style.background);
        } else {
            // set color to light mint
            console.log(this.style.background);
            this.style.background = "rgb(212, 242, 246)";
            console.log(this.style.background);
        }
    });
});

// process all user input fields and submit the form 
function submitSurvey() {
    // find user-selected genres 
    selectedGenres = [];
    genreButtons.forEach(function(btn) {
        // we know user has selected genre if the button is in mint
        if (btn.style.background === "rgb(162, 227, 236)") {
            selectedGenres.push(btn.textContent);
        }
    });
    console.log(selectedGenres);
    // get keywords string
    const keywordsStr = keywordInput.value;
    // get description string 
    const descString = descInput.value;
    console.log(keywordsStr);
    console.log(descString);
    const userInput = {
        "selected_genres": selectedGenres,
        "keywords": keywordsStr,
        "desc": descString,
    };
    console.log(userInput);
    // insert userInput value
    const submitWidget = document.getElementById('survey-data');
    submitWidget.value = JSON.stringify(userInput);
    surveyForm.submit();
}
