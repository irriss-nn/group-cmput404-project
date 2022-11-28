// TODO: Implement node auth
// TODO: Authenticate using database
function getCredentials(host) {
    if (host === 'https://socioecon.herokuapp.com')
        return `${btoa('team7:pot8os_are_yummy')}`

    return ''
}
