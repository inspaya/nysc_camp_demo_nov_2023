function recharge() {
    const endpoint = "/recharge";
    const phoneNumber = document.getElementById('phone_no').value;

    fetch(endpoint, {  
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({"phone_number": phoneNumber }),
    })
    .then(response => response.json())
    .then(data => console.log(data));
    // .catch(error => console.error('Error', error));
}