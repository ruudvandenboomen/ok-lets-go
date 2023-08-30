self.addEventListener('push', function (event) {
    const options = {
        body: event.data.text(),
        icon: 'https://ok-lets-go.ruudvandenboomen.nl//static/images/icon-96x96.png',
        badge: 'https://ok-lets-go.ruudvandenboomen.nl//static/images/icon-96x96.png',
        data: {
            url: 'https://ok-lets-go.ruudvandenboomen.nl/'
        }
    };
    console.log(event)
    event.waitUntil(
        self.registration.showNotification('Push Notification', options)
    );
});

self.addEventListener('notificationclick', function (event) {
    event.notification.close();

    const clickedUrl = event.notification.data.url;

    if (clickedUrl && clients.openWindow) {
        event.waitUntil(
            clients.openWindow(clickedUrl)
        );
    }
});