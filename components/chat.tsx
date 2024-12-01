// "use client";

// import { PreviewMessage, ThinkingMessage } from "@/components/message";
// import { MultimodalInput } from "@/components/multimodal-input";
// import { Overview } from "@/components/overview";
// import { useScrollToBottom } from "@/hooks/use-scroll-to-bottom";
// import { ToolInvocation } from "ai";
// import { useChat } from "ai/react";
// import { toast } from "sonner";

// export function Chat() {
//   const chatId = "001";

//   const {
//     messages,
//     setMessages,
//     handleSubmit,
//     input,
//     setInput,
//     append,
//     isLoading,
//     stop,
//   } = useChat({
//     maxSteps: 4,
//     initialMessages: [
//       {
//         id: "initial-greeting",
//         role: "assistant",
//         content:
//           "Welcome to the Highrise FAQ Bot! I'm here to help you with any questions about Highrise. What would you like to know?",
//       },
//     ],
//     headers: {
//       "Content-Type": "application/json",
//     },
//     onError: (error) => {
//       if (error.message.includes("Too many requests")) {
//         toast.error(
//           "You are sending too many messages. Please try again later."
//         );
//       }
//     },
//     onResponse: (response) => {
//       console.log("Response received:", response);
//     },
//   });

//   const [messagesContainerRef, messagesEndRef] =
//     useScrollToBottom<HTMLDivElement>();

//   async function handleCustomSubmit(event?: { preventDefault?: () => void }) {
//     if (event && event.preventDefault) {
//       event.preventDefault();
//     }

//     if (input.trim() === "") return;
//     console.log("input", input);

//     // Manually append the user message
//     append({
//       id: "123",
//       role: "user",
//       content: input,
//     });
//     // const response = await fetch("api/chat", {
//     //   method: "POST",
//     //   body: JSON.stringify({
//     //     messages: [...messages, { id: "123", role: "user", content: input }],
//     //   }),
//     // });
//     // const { messages: newMessages } = await response.json();

//     // setMessages((currentMessages) => [...currentMessages, ...newMessages]);

//     // Clear the input after sending
//     setInput("");
//   }

//   return (
//     <div className="flex flex-col min-w-0 h-[calc(100dvh-52px)] bg-background">
//       <div
//         ref={messagesContainerRef}
//         className="flex flex-col min-w-0 gap-6 flex-1 overflow-y-scroll pt-4"
//       >
//         {messages.length === 0 && <Overview />}

//         {messages.map((message, index) => (
//           <PreviewMessage
//             key={message.id}
//             chatId={chatId}
//             message={message}
//             isLoading={isLoading && messages.length - 1 === index}
//           />
//         ))}

//         {isLoading &&
//           messages.length > 0 &&
//           messages[messages.length - 1].role === "user" && <ThinkingMessage />}

//         <div
//           ref={messagesEndRef}
//           className="shrink-0 min-w-[24px] min-h-[24px]"
//         />
//       </div>

//       <form className="flex mx-auto px-4 bg-background pb-4 md:pb-6 gap-2 w-full md:max-w-3xl">
//         <MultimodalInput
//           chatId={chatId}
//           input={input}
//           setInput={setInput}
//           handleSubmit={handleCustomSubmit}
//           isLoading={isLoading}
//           stop={stop}
//           messages={messages}
//           setMessages={setMessages}
//           append={append}
//         />
//       </form>
//     </div>
//   );
// }
"use client";

import { PreviewMessage, ThinkingMessage } from "@/components/message";
import { MultimodalInput } from "@/components/multimodal-input";
import { Overview } from "@/components/overview";
import { useScrollToBottom } from "@/hooks/use-scroll-to-bottom";
import { ToolInvocation } from "ai";
import { useChat } from "ai/react";
import { toast } from "sonner";

export function Chat() {
  const chatId = "001";

  const {
    messages,
    setMessages,
    handleSubmit,
    input,
    setInput,
    append,
    isLoading,
    stop,
  } = useChat({
    maxSteps: 4,
    initialMessages: [
      {
        id: "initial-greeting",
        role: "assistant",
        content:
          "Welcome to the Highrise FAQ Bot! I'm here to help you with any questions about Highrise. What would you like to know?",
      },
    ],
    onError: (error) => {
      if (error.message.includes("Too many requests")) {
        toast.error(
          "You are sending too many messages. Please try again later."
        );
      }
    },
    onResponse: (response) => {
      console.log("Response received:", response);
    },
    streamProtocol: "text",
  });

  const [messagesContainerRef, messagesEndRef] =
    useScrollToBottom<HTMLDivElement>();

  return (
    <div className="flex flex-col min-w-0 h-[calc(100dvh-52px)] bg-background">
      <div
        ref={messagesContainerRef}
        className="flex flex-col min-w-0 gap-6 flex-1 overflow-y-scroll pt-4"
      >
        {messages.length === 0 && <Overview />}

        {messages.map((message, index) => (
          <PreviewMessage
            key={message.id}
            chatId={chatId}
            message={message}
            isLoading={isLoading && messages.length - 1 === index}
          />
        ))}

        {isLoading &&
          messages.length > 0 &&
          messages[messages.length - 1].role === "user" && <ThinkingMessage />}

        <div
          ref={messagesEndRef}
          className="shrink-0 min-w-[24px] min-h-[24px]"
        />
      </div>

      <form className="flex mx-auto px-4 bg-background pb-4 md:pb-6 gap-2 w-full md:max-w-3xl">
        <MultimodalInput
          chatId={chatId}
          input={input}
          setInput={setInput}
          handleSubmit={handleSubmit}
          isLoading={isLoading}
          stop={stop}
          messages={messages}
          setMessages={setMessages}
          append={append}
        />
      </form>
    </div>
  );
}
