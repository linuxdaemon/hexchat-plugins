hexchat.register("Snofilter", "0.1.0", "Companion script for https://github.com/TotallyNotRobots/znc-modules/blob/master/python/snofilter.py")

local function get_net()
  for ctx in hexchat.iterate("channels") do
    if ctx.type == 1 and ctx.network == hexchat.get_info("network") then
      return ctx.channel
    end
  end
end

local cmd_to_event = {
  ["NOTICE"] = "Notice",
  ["PRIVMSG"] = "Private Message to Dialog",
}

local function handle(word, word_eol)
  local window = word[1]:match("^:%*(.+)!snofilter@znc.in$")
  if not window then return end
  local net = get_net() .. "-snotices"
  local serv = hexchat.find_context(net)
  if not serv then
    hexchat.command("newserver -noconnect " .. net)
    serv = hexchat.find_context(net)
  end
  serv:command("query -nofocus " .. window)
  local window_ctx = hexchat.find_context(net, window)
  local event = cmd_to_event[word[2]]
  window_ctx:emit_print(event, window, word_eol[4]:sub(2))
  return hexchat.EAT_HEXCHAT
end

hexchat.hook_server("PRIVMSG", handle)
hexchat.hook_server("NOTICE", handle)
