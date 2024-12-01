// "use client";

// import type { ChatRequestOptions, CreateMessage, Message } from "ai";
// import { motion } from "framer-motion";
// import type React from "react";
// import {
//   useRef,
//   useState,
//   useEffect,
//   useCallback,
//   type Dispatch,
//   type SetStateAction,
// } from "react";
// import { toast } from "sonner";
// import { useLocalStorage, useWindowSize } from "usehooks-ts";

// import { cn, sanitizeUIMessages } from "@/lib/utils";

// import { ArrowUpIcon, StopIcon, ThumbUpIcon, ThumbDownIcon } from "./icons";
// import { Button } from "./ui/button";
// import { Textarea } from "./ui/textarea";

// const suggestedActions = [
//   {
//     title: "What is the weather",
//     label: "in San Francisco?",
//     action: "What is the weather in San Francisco?",
//   },
//   {
//     title: "How is python useful",
//     label: "for AI engineers?",
//     action: "How is python useful for AI engineers?",
//   },
// ];

// export function MultimodalInput({
//   chatId,
//   input,
//   setInput,
//   isLoading,
//   stop,
//   messages,
//   setMessages,
//   append,
//   handleSubmit,
//   className,
// }: {
//   chatId: string;
//   input: string;
//   setInput: (value: string) => void;
//   isLoading: boolean;
//   stop: () => void;
//   messages: Array<Message>;
//   setMessages: Dispatch<SetStateAction<Array<Message>>>;
//   append: (
//     message: Message | CreateMessage,
//     chatRequestOptions?: ChatRequestOptions
//   ) => Promise<string | null | undefined>;
//   handleSubmit: (
//     event?: {
//       preventDefault?: () => void;
//     },
//     chatRequestOptions?: ChatRequestOptions
//   ) => void;
//   className?: string;
// }) {
//   const textareaRef = useRef<HTMLTextAreaElement>(null);
//   const { width } = useWindowSize();

//   const [isChatEnded, setIsChatEnded] = useState(false);

//   const [feedback, setFeedback] = useState<{ helpful: boolean | null }>({
//     helpful: null,
//   });

//   useEffect(() => {
//     if (textareaRef.current) {
//       adjustHeight();
//     }
//   }, []);

//   const endChat = useCallback(() => {
//     // Clear messages and show farewell
//     setMessages([]);
//     setIsChatEnded(true);
//     append({
//       role: "assistant",
//       content:
//         "Thanks for chatting! If you need further assistance, please visit the Highrise support page at https://support.highrise.game/en/. Have a great day!",
//     });

//     // Reset local storage and input
//     setInput("");
//     setLocalStorageInput("");
//   }, [setMessages, append, setInput]);

//   const adjustHeight = () => {
//     if (textareaRef.current) {
//       textareaRef.current.style.height = "auto";
//       textareaRef.current.style.height = `${
//         textareaRef.current.scrollHeight + 2
//       }px`;
//     }
//   };

//   const [localStorageInput, setLocalStorageInput] = useLocalStorage(
//     "input",
//     ""
//   );

//   useEffect(() => {
//     if (textareaRef.current) {
//       const domValue = textareaRef.current.value;
//       // Prefer DOM value over localStorage to handle hydration
//       const finalValue = domValue || localStorageInput || "";
//       setInput(finalValue);
//       adjustHeight();
//     }
//     // Only run once after hydration
//     // eslint-disable-next-line react-hooks/exhaustive-deps
//   }, []);

//   useEffect(() => {
//     setLocalStorageInput(input);
//   }, [input, setLocalStorageInput]);

//   const handleInput = (event: React.ChangeEvent<HTMLTextAreaElement>) => {
//     setInput(event.target.value);
//     adjustHeight();
//   };

//   const submitForm = useCallback(() => {
//     handleSubmit();
//     setLocalStorageInput("");

//     console.log("Current Messages:", messages);

//     if (width && width > 768) {
//       textareaRef.current?.focus();
//     }
//   }, [handleSubmit, setLocalStorageInput, width]);

//   const submitFeedback = (helpful: boolean) => {
//     if (!messages.length) {
//       toast.error("No message to provide feedback on.");
//       return;
//     }

//     const lastMessage = messages[messages.length - 1];

//     setFeedback({ helpful });
//     fetch("/api/feedback", {
//       method: "POST",
//       headers: { "Content-Type": "application/json" },
//       body: JSON.stringify({
//         chatId,
//         message: lastMessage,
//         helpful,
//       }),
//     })
//       .then((res) => {
//         if (res.ok) {
//           toast.success("Thanks for your feedback!");
//         } else {
//           throw new Error("Failed to submit feedback");
//         }
//       })
//       .catch((error) => {
//         toast.error("Failed to submit feedback. Please try again.");
//         console.error("Error in submitFeedback:", error);
//       });
//   };

//   return (
//     <div className="relative w-full flex flex-col gap-4">
//       {isChatEnded && (
//         <div className="text-center text-muted-foreground p-4">
//           Chat has ended. Start a new conversation by typing a message.
//         </div>
//       )}

//       {messages.length === 0 && !isChatEnded && (
//         <div className="grid sm:grid-cols-2 gap-2 w-full">
//           {suggestedActions.map((suggestedAction, index) => (
//             <motion.div
//               initial={{ opacity: 0, y: 20 }}
//               animate={{ opacity: 1, y: 0 }}
//               exit={{ opacity: 0, y: 20 }}
//               transition={{ delay: 0.05 * index }}
//               key={`suggested-action-${suggestedAction.title}-${index}`}
//               className={index > 1 ? "hidden sm:block" : "block"}
//             >
//               <Button
//                 variant="ghost"
//                 onClick={async () => {
//                   append({
//                     role: "user",
//                     content: suggestedAction.action,
//                   });
//                   setIsChatEnded(false);
//                 }}
//                 className="text-left border rounded-xl px-4 py-3.5 text-sm flex-1 gap-1 sm:flex-col w-full h-auto justify-start items-start"
//               >
//                 <span className="font-medium">{suggestedAction.title}</span>
//                 <span className="text-muted-foreground">
//                   {suggestedAction.label}
//                 </span>
//               </Button>
//             </motion.div>
//           ))}
//         </div>
//       )}

//       <Textarea
//         ref={textareaRef}
//         placeholder="Send a message..."
//         value={input}
//         onChange={handleInput}
//         className={cn(
//           "min-h-[24px] max-h-[calc(75dvh)] overflow-hidden resize-none rounded-xl !text-base bg-muted",
//           className
//         )}
//         rows={3}
//         autoFocus
//         onKeyDown={(event) => {
//           if (event.key === "Enter" && !event.shiftKey) {
//             event.preventDefault();

//             if (isLoading) {
//               toast.error("Please wait for the model to finish its response!");
//             } else {
//               submitForm();
//             }
//           }
//         }}
//       />

//       <Button onClick={endChat} className="mt-4 text-sm">
//         End Chat
//       </Button>

//       {messages.length > 0 && feedback.helpful === null && (
//         <div className="flex gap-2 justify-end mt-2">
//           <Button
//             variant="ghost"
//             onClick={() => submitFeedback(true)}
//             className="flex items-center gap-1"
//           >
//             <ThumbUpIcon size={16} /> Helpful
//           </Button>
//           <Button
//             variant="ghost"
//             onClick={() => submitFeedback(false)}
//             className="flex items-center gap-1"
//           >
//             <ThumbDownIcon size={16} /> Not Helpful
//           </Button>
//         </div>
//       )}

//       {isLoading ? (
//         <Button
//           className="rounded-full p-1.5 h-fit absolute bottom-2 right-2 m-0.5 border dark:border-zinc-600"
//           onClick={(event) => {
//             event.preventDefault();
//             stop();
//             setMessages((messages) => sanitizeUIMessages(messages));
//           }}
//         >
//           <StopIcon size={14} />
//         </Button>
//       ) : (
//         <Button
//           className="rounded-full p-1.5 h-fit absolute bottom-2 right-2 m-0.5 border dark:border-zinc-600"
//           onClick={(event) => {
//             event.preventDefault();
//             submitForm();
//           }}
//           disabled={input.length === 0}
//         >
//           <ArrowUpIcon size={14} />
//         </Button>
//       )}
//     </div>
//   );
// }

"use client";

import type { ChatRequestOptions, CreateMessage, Message } from "ai";
import { motion } from "framer-motion";
import type React from "react";
import {
  useRef,
  useEffect,
  useCallback,
  type Dispatch,
  type SetStateAction,
} from "react";
import { toast } from "sonner";
import { useLocalStorage, useWindowSize } from "usehooks-ts";

import { cn, sanitizeUIMessages } from "@/lib/utils";

import { ArrowUpIcon, StopIcon } from "./icons";
import { Button } from "./ui/button";
import { Textarea } from "./ui/textarea";

const suggestedActions = [
  {
    title: "What is the weather",
    label: "in San Francisco?",
    action: "What is the weather in San Francisco?",
  },
  {
    title: "How is python useful",
    label: "for AI engineers?",
    action: "How is python useful for AI engineers?",
  },
];

export function MultimodalInput({
  chatId,
  input,
  setInput,
  isLoading,
  stop,
  messages,
  setMessages,
  append,
  handleSubmit,
  className,
}: {
  chatId: string;
  input: string;
  setInput: (value: string) => void;
  isLoading: boolean;
  stop: () => void;
  messages: Array<Message>;
  setMessages: Dispatch<SetStateAction<Array<Message>>>;
  append: (
    message: Message | CreateMessage,
    chatRequestOptions?: ChatRequestOptions
  ) => Promise<string | null | undefined>;
  handleSubmit: (
    event?: {
      preventDefault?: () => void;
    },
    chatRequestOptions?: ChatRequestOptions
  ) => void;
  className?: string;
}) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const { width } = useWindowSize();

  useEffect(() => {
    if (textareaRef.current) {
      adjustHeight();
    }
  }, []);

  const adjustHeight = () => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${
        textareaRef.current.scrollHeight + 2
      }px`;
    }
  };

  const [localStorageInput, setLocalStorageInput] = useLocalStorage(
    "input",
    ""
  );

  useEffect(() => {
    if (textareaRef.current) {
      const domValue = textareaRef.current.value;
      // Prefer DOM value over localStorage to handle hydration
      const finalValue = domValue || localStorageInput || "";
      setInput(finalValue);
      adjustHeight();
    }
    // Only run once after hydration
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    setLocalStorageInput(input);
  }, [input, setLocalStorageInput]);

  const handleInput = (event: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInput(event.target.value);
    adjustHeight();
  };

  const submitForm = useCallback(() => {
    handleSubmit(undefined, {});
    setLocalStorageInput("");

    if (width && width > 768) {
      textareaRef.current?.focus();
    }
  }, [handleSubmit, setLocalStorageInput, width]);

  return (
    <div className="relative w-full flex flex-col gap-4">
      {messages.length === 0 && (
        <div className="grid sm:grid-cols-2 gap-2 w-full">
          {suggestedActions.map((suggestedAction, index) => (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 20 }}
              transition={{ delay: 0.05 * index }}
              key={`suggested-action-${suggestedAction.title}-${index}`}
              className={index > 1 ? "hidden sm:block" : "block"}
            >
              <Button
                variant="ghost"
                onClick={async () => {
                  append({
                    role: "user",
                    content: suggestedAction.action,
                  });
                }}
                className="text-left border rounded-xl px-4 py-3.5 text-sm flex-1 gap-1 sm:flex-col w-full h-auto justify-start items-start"
              >
                <span className="font-medium">{suggestedAction.title}</span>
                <span className="text-muted-foreground">
                  {suggestedAction.label}
                </span>
              </Button>
            </motion.div>
          ))}
        </div>
      )}

      <Textarea
        ref={textareaRef}
        placeholder="Send a message..."
        value={input}
        onChange={handleInput}
        className={cn(
          "min-h-[24px] max-h-[calc(75dvh)] overflow-hidden resize-none rounded-xl !text-base bg-muted",
          className
        )}
        rows={3}
        autoFocus
        onKeyDown={(event) => {
          if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();

            if (isLoading) {
              toast.error("Please wait for the model to finish its response!");
            } else {
              submitForm();
            }
          }
        }}
      />

      {isLoading ? (
        <Button
          className="rounded-full p-1.5 h-fit absolute bottom-2 right-2 m-0.5 border dark:border-zinc-600"
          onClick={(event) => {
            event.preventDefault();
            stop();
            setMessages((messages) => sanitizeUIMessages(messages));
          }}
        >
          <StopIcon size={14} />
        </Button>
      ) : (
        <Button
          className="rounded-full p-1.5 h-fit absolute bottom-2 right-2 m-0.5 border dark:border-zinc-600"
          onClick={(event) => {
            event.preventDefault();
            submitForm();
          }}
          disabled={input.length === 0}
        >
          <ArrowUpIcon size={14} />
        </Button>
      )}
    </div>
  );
}
