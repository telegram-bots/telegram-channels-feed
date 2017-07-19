print("STARTED HANDLER INITIALISATION")

ROUTING_KEY = "#"
HOST = "rabbit"
PORT = 5672

local cjson = require("cjson")
local amqp = require("amqp")
local channel
local connection = {
    role = "publisher",
    routing_key = ROUTING_KEY,
    exchange = "channels_feed",
    queue = "channels_feed.single"
}
local exchange = {
    typ = "direct",
    durable = true
}
local queue = {
    durable = true,
    auto_delete = false,
    no_wait = false
}
local properties = {
    content_type = "application/json",
    content_encoding = "utf-8",
    delivery_mode = 2
}

-- Sleep for given time
function sleep(seconds)
    local sec = tonumber(os.clock() + seconds);
    while (os.clock() < sec) do
    end
end

-- Try to connect to AMQP until success
function connect()
    print("Connecting to AMQP...")

    if channel ~= nil then
        channel:teardown()
        channel = nil
    end

    channel = amqp.new(connection)

    local conn_ok, conn_err = channel:connect(HOST, PORT)
    while conn_ok == nil do
        print("CONNECTION LOST: " .. conn_err .. ". TRYING TO RECONNECT...")
        sleep(5)
        conn_ok = channel:connect(HOST, PORT)
    end

    local init_ok, init_err = channel:setup()
    while init_ok == nil do
        print("INITIALISATION FAILED: " .. init_err ..  ". TRYING AGAIN...")
        sleep(5)
        init_ok = channel:setup()
    end
    print("Connected to AMQP")
end

-- Declare exchange, queue and bind them
function declare()
    channel:exchange_declare(exchange)
    print("Exchange successfully declared")

    channel:queue_declare(queue)
    print("Queue successfully declared")

    channel:queue_bind({routing_key = ROUTING_KEY})
    print("Exchange successfully bound to queue")
end

connect()
declare()

print("HANDLER INITIALISATION COMPLETE")

-- Send message to AMQP exchange
function send_to_exchange(msg)
    local res, err = channel:publish(msg, {}, properties)
    while res ~= true do
        print("Error sending to exchange: " .. err)
        sleep(5)
        if err:find("closed") then
            connect()
        end
        res, err = channel:publish(msg, {}, properties)
    end
    print("Successfully sent to exchange")
end

-- View message and mark as read
function mark_as_read(chat_id, msg_id)
    tdcli_function ({
        ID = "ViewMessages",
        chat_id_ = chat_id,
        message_ids_ = {msg_id}
    }, db_cb, nil)
end

-- Reply to user
function reply(chat_id, msg_id, text)
    tdcli_function ({
        ID="SendMessage",
        chat_id_=chat_id,
        reply_to_message_id_=msg_id,
        disable_notification_=0,
        from_background_=1,
        reply_markup_=nil,
        input_message_content_={
            ID="InputMessageText",
            text_=text,
            disable_web_page_preview_=1,
            clear_draft_=0,
            entities_={}
        }
    }, dl_cb, nil)
end

-- telegram-cli default
function dl_cb(arg, data)
end

-- telegram-cli message callback
function tdcli_update_callback(data)
    if (data.ID == "UpdateNewMessage") then
        local msg = data.message_

        if (msg.is_post_ == true) then
            send_to_exchange(cjson.encode(msg))
            mark_as_read(msg.chat_id_, msg.id_)
        elseif msg.content_.ID == "MessageText" then
            if msg.content_.text_:lower() == "ping" then
                reply(msg.chat_id_, msg.id_, "pong")
            end
        end
    elseif (data.ID == "UpdateMessageContent") then
        send_to_exchange(cjson.encode(data))
    end
end
