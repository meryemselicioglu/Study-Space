function relay(id) {
    var text = document.getElementById(id).innerHTML;
    console.log(text);
    //split text into 2 strings; name and location
    var roomName = split[0];

    //alert(roomName);
    //alert(roomLocation);

}

function setadmin() {
    let user1 = document.getElementById("email").innerHTML;
    user1 = user1.substring(7);
    console.log(user1);
    window.location.href= "{{ url_for('adminusers', user=#user#) }}".replace('#user#', user1);
}