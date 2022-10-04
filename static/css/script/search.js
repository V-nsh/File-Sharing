const searchht = () => {
    const filter = document.getElementById('myInput').value.toUpperCase();
    const store = document.getElementById("list");
    const prod = document.querySelectorAll(".row");
    const pname = store.getElementsByTagName("h4");

    for (var i = 0; i < pname.length; i++) {
        let a = prod[i].getElementsByTagName('h4')[0];
        if (a) {
            let textValue = a.textContent || a.innerHTML;

            if (textValue.toUpperCase().indexOf(filter) > -1) {
                prod[i].style.display = '';
            } else {
                prod[i].style.display = 'none';
            }
        }
    }
}