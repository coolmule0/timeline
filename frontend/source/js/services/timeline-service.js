export default class {
  static getEntries(date) {
    const requestUrl = new URL('/api/timeline/entries/', `https://${window.location.hostname}`);
    requestUrl.search = new URLSearchParams({
        date_on_timeline__gte: moment(date).startOf('day').toJSON(),
        date_on_timeline__lt: moment(date).startOf('day').add(1, 'day').toJSON(),
    });
    return fetch(requestUrl).then((response) => {
      return response.json();
    });
  }

  static saveEntry(entry){
    let url = '/api/timeline/entries/';
    let method = 'POST';
    if(entry.id !== null && entry.id !== undefined){
      url += entry.id + '/';
      method = 'PUT';
    }
    const requestUrl = new URL(url, `https://${window.location.hostname}`);
    return fetch(
      requestUrl,
      { 
        method: method,
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(entry),
      }
    ).then((response) => {
      return response.json();
    });
  }
}