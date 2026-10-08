import { useGettext } from 'vue3-gettext'

export function useErrors() {
  const { $gettext } = useGettext()

  function errorText(error) {
    if (!error || error.status === undefined) return $gettext('Unexpected error.')
    switch (error.status) {
      case 0:
        return $gettext('The server cannot be reached.')
      case 400:
        return $gettext('The request was rejected. Please check your input or the link.')
      case 401:
        return $gettext('Authentication failed.')
      case 403:
        return $gettext('You are not allowed to do this.')
      case 404:
        return $gettext('Not found.')
      case 409:
        return $gettext('This entry already exists.')
      case 422:
        return $gettext('Invalid input.')
      case 423:
        return error.retryAfter
          ? $gettext('Too many failed attempts. Try again in %{minutes} minute(s).', {
              minutes: Math.ceil(error.retryAfter / 60),
            })
          : $gettext('Too many failed attempts. Please try again later.')
      default:
        return $gettext('Unexpected error.')
    }
  }

  return { errorText }
}
