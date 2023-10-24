// Popovers that stays while on popover bubble
// https://stackoverflow.com/questions/15989591/how-can-i-keep-bootstrap-popover-alive-while-the-popover-is-being-hovered
$('[data-toggle="popover"]')
  .popover({
    trigger: "manual",
    html: true,
    animation: false,
    placement: "auto"
  })
  .on("mouseenter", function() {
    var _this = this
    $(this).popover("show")
    $(".popover").on("mouseleave", function() {
      $(_this).popover("hide")
    })
  })
  .on("mouseleave", function() {
    var _this = this
    setTimeout(function() {
      if (!$(".popover:hover").length) {
        $(_this).popover("hide")
      }
    }, 100)
  })

// Open links found in error description in a new window/tab
$("body").on("mouseover", "div.popover a", function() {
  $(this).prop("title", "Ouvrir dans une nouvelle fenêtre")
})
$("body").on("click", "div.popover a", function() {
  var url = $(this).prop("href")
  window.open(url, "_blank")
  return false
})
