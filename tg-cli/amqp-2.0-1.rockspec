package = "amqp"
version = "2.0-1"
source = {
  url = "git://github.com/ZigzagAK/amqp.git"
}
description = {
  summary = "Lua Client for AMQP 0.9.1",
  homepage = "https://github.com/ZigzagAK/amqp",
  license = "APACHE-2.0",
}
dependencies = {
  "lua >= 5.1",
  "luabitop",
  "luasocket"
}
build = {
  type = "builtin",
  modules = {
   ["amqp"] = "lib/amqp/amqp.lua",
   ["buffer"] = "lib/amqp/buffer.lua",
   ["frame"] = "lib/amqp/frame.lua",
   ["logger"] = "lib/amqp/logger.lua",
   ["consts"] = "lib/amqp/consts.lua"
  }
}
