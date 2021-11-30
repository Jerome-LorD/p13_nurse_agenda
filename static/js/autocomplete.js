$(function () {
  $('#newcabinet')
    .autocomplete({
      minLength: 2,
      source: autocomp_source,
      focus: function (event, ui) {
        $('#newcabinet').val(ui.item.name)
        return false
      },
      select: function (event, ui) {
        $('#newcabinet').val(ui.item.name)
        $('#newcabinet-id').val(ui.item.value)
        $(this).closest('form').submit()
        return false
      },
    })
    .autocomplete('instance')._renderItem = function (ul, item) {
    return $('<li>')
      .append('<div>' + item.name + '</div>')
      .appendTo(ul)
  }
})
