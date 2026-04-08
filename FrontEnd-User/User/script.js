function gotopage(){
    window.location.href="index.html"
}

fetch("navbar.html")
.then(res => res.text())
.then (data => {
    document.getElementById("header").innerHTML=data;
});

function goToHome() {
    window.location.href="home.html";
}