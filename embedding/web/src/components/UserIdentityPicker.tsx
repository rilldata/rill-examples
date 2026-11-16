"use client";

import { useState } from "react";

// Demo users shared by the per-user state examples. Using the same IDs on
// every page lets you see, for example, that a report created as Alice is
// visible on Alice's pages but not on Bob's.
export const DEMO_USER_IDS = ["user-alice-123", "user-bob-456"];

interface UserIdentityPickerProps {
  userIds?: string[];
  userId: string;
  onUserIdChange: (userId: string) => void;
  // When provided, renders an optional email input. The value is only
  // committed on blur or Enter, so typing doesn't request a new iframe on
  // every keystroke.
  email?: string;
  onEmailChange?: (email: string) => void;
  emailHint?: React.ReactNode;
}

const UserIdentityPicker = ({
  userIds = DEMO_USER_IDS,
  userId,
  onUserIdChange,
  email,
  onEmailChange,
  emailHint,
}: UserIdentityPickerProps) => {
  const [draftEmail, setDraftEmail] = useState(email ?? "");
  const commitEmail = () => onEmailChange?.(draftEmail.trim());

  return (
    <div className="space-y-4">
      <div>
        <h3 className="text-sm font-semibold text-gray-700 mb-2">
          Select user
        </h3>
        <div className="flex gap-2">
          {userIds.map((id) => (
            <button
              key={id}
              onClick={() => onUserIdChange(id)}
              className={`px-4 py-2 rounded-lg text-sm font-medium border ${
                userId === id
                  ? "bg-indigo-600 text-white border-indigo-600"
                  : "bg-white text-gray-700 border-gray-300 hover:bg-gray-100"
              }`}
            >
              {id}
            </button>
          ))}
        </div>
      </div>

      {onEmailChange && (
        <div>
          <label
            htmlFor="user-email"
            className="block text-sm font-semibold text-gray-700 mb-2"
          >
            User email (optional)
          </label>
          <input
            id="user-email"
            type="email"
            placeholder="john@example.com"
            value={draftEmail}
            onChange={(e) => setDraftEmail(e.target.value)}
            onBlur={commitEmail}
            onKeyDown={(e) => {
              if (e.key === "Enter") commitEmail();
            }}
            className="w-80 px-3 py-2 rounded-lg text-sm border border-gray-300 focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
          {emailHint && (
            <p className="text-xs text-gray-500 mt-1">{emailHint}</p>
          )}
        </div>
      )}
    </div>
  );
};

export default UserIdentityPicker;
