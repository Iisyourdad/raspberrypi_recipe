function scrollToRecipes() {
    var element = document.getElementById("recipes-section");
    if(element) {
        window.scrollTo({
            top: element.offsetTop,
            behavior: 'smooth'
        });
    }
}
