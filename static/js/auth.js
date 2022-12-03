async function getCredentials(host) {
    let credentials = ''
    await fetch(`/service/credentials/${btoa(host)}`)
        .then(response => response.json())
        .then(data => {
            credentials = btoa(`${data.username}:${data.password}`);
        });

    return credentials;
}
