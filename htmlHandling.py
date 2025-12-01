# CSS styling for the chat messages and sidebar
css = '''
<style>
/* Overall chat container and sidebar styles */
.sidebar-container {
    position: fixed;
    top: 0; right: 0;
    width: 350px; /* Adjust the width of the sidebar as needed */
    height: 100vh; /* Full-height sidebar */
    padding: 20px;
    background-color: #f8f9fa; /* Lighter background color for the sidebar */
    overflow-y: auto; /* Enable vertical scroll */
    /* Enhanced box shadow for a smoother look */
    box-shadow: -2px 0px 10px rgba(0, 0, 0, 0.05);
}

/* Simplify the chat-message class to share base styles */
.chat-message {
    padding: 10px 15px; /* Moderate padding around messages */
    border-radius: 20px; /* Rounded corners for chat bubbles */
    margin-bottom: 12px; /* Space between messages */
    display: flex; /* Flex layout for avatar and message */
    align-items: center; /* Vertical centering */
}

/* User message styles */
.chat-message.user {
    background-color: #007bff; /* Bootstrap primary blue */
    color: #ffffff; /* White text for readability */
    margin-left: auto; /* Align user messages to the right */
}

/* Bot message styles */
.chat-message.bot {
    background-color: #e9ecef; /* Bootstrap secondary background color */
    color: #343a40; /* Bootstrap dark gray for contrast */
}

/* Restructure avatar as a separate element */
.avatar img {
    width: 40px; /* Fixed width for avatar images */
    height: 40px; /* Fixed height for avatar images */
    border-radius: 50%; /* Circular avatars */
    margin-right: 10px; /* Space between avatar and message */
}

/* Ensure message text fits well */
.message {
    flex: 1; /* Allow message text to flexibly fill the space */
    padding: 0 10px; /* Padding inside the message bubble */
    word-break: break-word; /* Break overly long words */
}
</style>
'''

#  HTML template for the bot's message
bot_template = '''
<div class="chat-message bot">
    <div class="avatar">
        <img src="https://th.bing.com/th?q=Icon+of+Computer&w=120&h=120&c=1&rs=1&qlt=90&cb=1&dpr=1.1&pid=InlineBlock&mkt=en-XA&cc=EG&setlang=en&adlt=strict&t=1&mw=247" alt="Bot Avatar">
    </div>
    <div class="message">{{MSG}}</div>
</div>
'''

# HTML template for the user's message
user_template = '''
<div class="chat-message user">
    <div class="avatar">
        <img src="https://th.bing.com/th?q=Simple+Icon&w=120&h=120&c=1&rs=1&qlt=90&cb=1&dpr=1.1&pid=InlineBlock&mkt=en-XA&cc=EG&setlang=en&adlt=strict&t=1&mw=247" alt="User Avatar">
    </div>    
    <div class="message">{{MSG}}</div>
</div>
'''
