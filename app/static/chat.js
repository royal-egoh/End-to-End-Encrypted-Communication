const token = localStorage.getItem("token");
if (!token) {
    window.location.href = "/login";
}

// jwt
const payload = JSON.parse(atob(token.split(".")[1]));
const myUsername = payload.sub;
let myId = null;
let currentRecipient = null;
let ws = null;

setTimeout(() => {
    if (!ws) {
        init();
    }
}, 3000);

//?global var for ping interval
let pingInterval = null;
document.getElementById("logged-user").textContent = myUsername;

//main init
async function init() {
    const userResponse = await fetch(`/users/${myUsername}/public_key`, {
        headers: {"Authorization": `Bearer ${token}`}
    });
    const userData = await userResponse.json();
    myId = userData.id;

    await loadConversations();



    ws = new WebSocket(`ws://127.0.0.1:8000/ws?token=${token}`);
    ws.onopen = () => console.log("WebSocket connected");
    ws.onerror = (e) => console.log("WebSocket error", e);
    ws.onclose = function() {
        console.log("WebSocket closed, reconnecting...");
    };

    if (pingInterval) {
        clearInterval(pingInterval);
    }
    //*ping to keep connection alive
    pingInterval = setInterval(() => {
        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({type: "ping"}));
        }
    }, 30000);


    ws.onmessage = async function(event) {
        const msg = JSON.parse(event.data);
        if (currentRecipient && msg.sender_id === currentRecipient.id) {
            const decrypted = await decryptMessage(msg.content_for_recipient);
            appendMessage(decrypted, false);
        }
    };
    //search input
    
}

document.getElementById("search-input").addEventListener("keydown", async function(event) {
        if (event.key === "Enter") {
            const username = this.value.trim();
            if (!username) return;
            if (username === myUsername) {
                alert("You cannot chat with yourself.");
                return;
            }

            const response = await fetch(`/users/${username}/public_key`, {
                headers: {"Authorization": `Bearer ${token}`}
            });
            if (response.ok) {
                const user = await response.json();
                openChat(user);
            } else {
                alert("User not found.");
            }
        }
    });
//date separator
function addDateSeparator(container, timestamp) {
    const date = new Date(timestamp);
    const today = new Date();
    const yesterday = new Date();
    yesterday.setDate(today.getDate() - 1);

    let label;
    if (date.toDateString() === today.toDateString()) label = "Today";
    else if (date.toDateString() === yesterday.toDateString()) label = "Yesterday";
    else label = date.toLocaleDateString([], {day: "numeric", month: "long", year: "numeric"});

    const sep = document.createElement("div");
    sep.className = "date-separator";
    sep.innerHTML = `<span>${label}</span>`;
    container.appendChild(sep);
}

//conversations
    async function loadConversations() {
    const response = await fetch(`/users/${myUsername}/conversations`, {
        headers: { "Authorization": `Bearer ${token}` }
    });

    const conversations = await response.json();

    const userList = document.getElementById("user-list");
    userList.innerHTML = "";

    for (const user of conversations) {
        if (user.username === myUsername) continue;

        let preview = "Click to chat";

        if (user.last_message) {
            try {
                const decrypted = await decryptMessage(user.last_message);
                preview = decrypted.slice(0, 15);
            } catch (e) {
                preview = "[encrypted]";
            }
        }

        const div = document.createElement("div");
        div.className = "user";

        div.innerHTML = `
            <div class="header-avatar">${user.username[0].toUpperCase()}</div>
            <div class="user-info">
                <div class="username">${user.username}</div>
                <div class="preview">${preview}...</div>
            </div>
        `;

        div.onclick = () => openChat(user);
        userList.appendChild(div);
    }
}

    // open a chat
    async function openChat(user) {
        currentRecipient = user;
        document.getElementById("chat-username").textContent = user.username;
        document.getElementById("header-avatar").textContent = user.username[0].toUpperCase();

        const response = await fetch(`/messages/history/${user.username}`, {
            headers: {"Authorization": `Bearer ${token}`}
        });
        const messages = await response.json();
        displayMessages(messages);
    }

    //message history
    async function displayMessages(messages) {
        const container = document.getElementById("messages");
        container.innerHTML = "";
        let lastDate = null;

        for (const msg of messages) {
            const msgDate = new Date(msg.timestamp).toDateString();
            if (msgDate !== lastDate) {
                addDateSeparator(container, msg.timestamp);
                lastDate = msgDate;
            }
            const div = document.createElement("div");
            const isSent = msg.sender_id === myId;
            div.className = `msg ${isSent ? "sent" : "received"}`;
            const time = new Date(msg.timestamp).toLocaleTimeString([], {
                hour: "2-digit", minute: "2-digit"
            });

            let content = "";
            try {
                const encryptedContent = isSent ? msg.content_for_sender : msg.content_for_recipient;
                content = await decryptMessage(encryptedContent);
            } catch(e) {
                content = "[encrypted]"; //?
            }

            div.innerHTML = `${content}<span class="time">${time}</span>`;
            container.appendChild(div);
        }
        container.scrollTop = container.scrollHeight;
    }

    //message appending
    function appendMessage(content, isSent) {
        const container = document.getElementById("messages");
        const div = document.createElement("div");
        div.className = `msg ${isSent ? "sent" : "received"}`;
        const time = new Date().toLocaleTimeString([], {
            hour: "2-digit", minute: "2-digit"
        });
        div.innerHTML = `${content}<span class="time">${time}</span>`;
        container.appendChild(div);
        container.scrollTop = container.scrollHeight;
    }

    async function encryptMessage(text, recipientUsername) {
    // encrypt for recipient
        const recipientResponse = await fetch(`/users/${recipientUsername}/public_key`, {
            headers: {"Authorization": `Bearer ${token}`}
        });
        const recipientData = await recipientResponse.json();
        const contentForRecipient = await encryptWithKey(text, recipientData.public_key);

        // encrypt for senderr
        const senderResponse = await fetch(`/users/${myUsername}/public_key`, {
            headers: {"Authorization": `Bearer ${token}`}
        });
        const senderData = await senderResponse.json();
        const contentForSender = await encryptWithKey(text, senderData.public_key);

        return {contentForRecipient, contentForSender};
    }

    async function encryptWithKey(text, publicKeyBase64) {
        const publicKeyBuffer = Uint8Array.from(atob(publicKeyBase64), c => c.charCodeAt(0));
        const publicKey = await window.crypto.subtle.importKey("spki", publicKeyBuffer,{name: "RSA-OAEP", hash: "SHA-256"},false, ["encrypt"]);
        const encoded = new TextEncoder().encode(text);
        const encrypted = await window.crypto.subtle.encrypt(
            {name: "RSA-OAEP"}, publicKey, encoded
        );
        return btoa(String.fromCharCode(...new Uint8Array(encrypted)));
}

    // decropt message with my private key
    async function decryptMessage(encryptedContent) {
        const privateKeyStr = localStorage.getItem(`private_key_${myUsername}`);
        if (!privateKeyStr){
            throw new Error("Private Key Not Found")
            
        }
        const privateKeyBytes = Uint8Array.from(atob(privateKeyStr),c => c.charCodeAt(0));

        const privateKeyBuffer = privateKeyBytes.buffer;
        const privateKey = await window.crypto.subtle.importKey(
            "pkcs8", privateKeyBuffer,
            {name: "RSA-OAEP", hash: "SHA-256"},
            false, ["decrypt"]
        );

        const encryptedBuffer = Uint8Array.from(atob(encryptedContent), c => c.charCodeAt(0));
        const decrypted = await window.crypto.subtle.decrypt(
            {name: "RSA-OAEP"}, privateKey, encryptedBuffer
        );
        return new TextDecoder().decode(decrypted);
    }

    //on submitt
    document.getElementById("message-form").addEventListener("submit", async function(event) {
        event.preventDefault();
        const input = document.getElementById("message-input");
        const text = input.value.trim();
        if (!text || !currentRecipient) return;

        const encoded = new TextEncoder().encode(text);

        if (encoded.length > 190) {
            alert("Message is too long. Maximum is about 190 bytes.");
            return;
        }

        const {contentForRecipient, contentForSender} = await encryptMessage(text, currentRecipient.username);
        
        if (!ws || ws.readyState !== WebSocket.OPEN) {
            console.log("Reconnecting websocket...");

            ws = new WebSocket(`ws://127.0.0.1:8000/ws?token=${token}`);

            ws.onopen = () => {
                console.log("Reconnected.");
        
            ws.send(JSON.stringify({
                recipient_id: currentRecipient.id,
                content_for_recipient: contentForRecipient,
                content_for_sender: contentForSender
            }));
    };

    return;
}


        ws.send(JSON.stringify({
        recipient_id: currentRecipient.id,
        content_for_recipient: contentForRecipient,
        content_for_sender: contentForSender
        }));
        appendMessage(text, true);
        input.value = "";
    });

    init();
    // 
    
