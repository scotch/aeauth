

.aeauth-form.row
  % include "partials/messages.html"
  .span5
    header
      h4 | To get started, login with one of your existing accounts.
    ul
      % for p, u in providers.items()
        li.provider-btn > a.btn href="{{ u }}" > img src="/auth/static/img/{{ p }}.png" /
  .span4
    header
      h4 | Or create a new one.
    .password-form.form-horizontal
      form method="POST" action="/auth/password"
        fieldset.control-group
          label.control-label for="email" > strong | Email
          .controls > input type="text" name="email" /
        fieldset.control-group
          label.control-label for="password" > strong | Password
          .controls > input type="password" name="password" /
        fieldset.form-actions
          button.btn type="submit" | Login
        fieldset.control-group
          .controls >  p > small > a href="/account/recovery" | Can't access your account?
