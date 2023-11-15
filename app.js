const checkBox = document.getElementById("check");
const textBox = document.getElementById("phone_no");
const recharge_btn = document.getElementById("recharge_btn");

checkBox.addEventListener("change", function () {
    textBox.type = checkBox.checked ? 'password' : 'number';
});

recharge_btn.addEventListener("click", function checkInput() {
    let textValue = textBox.value.toString();

    if (textValue.length === 11 && (textValue.startsWith('07') || textValue.startsWith('08') || textValue.startsWith('09'))) {
        recharge();
    } else {
        alert("Incorrect number detected");
    }
});

function recharge() {
    const endpoint = "/recharge";
    const phoneNumber = document.getElementById('phone_no').value;

    fetch(endpoint, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ "phone_number": phoneNumber }),
    })
        .then(response => response.json())

        .then(data => console.log(data));
}

