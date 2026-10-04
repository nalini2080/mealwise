import { useEffect, useRef } from "react";

// Native <dialog>: gives focus trapping, Esc-to-close and a backdrop for free.
export default function Modal({ title, onClose, children }) {
  const ref = useRef(null);

  useEffect(() => {
    const dialog = ref.current;
    dialog.showModal();
    return () => dialog.close();
  }, []);

  return (
    <dialog
      ref={ref}
      className="modal"
      onCancel={(e) => {
        e.preventDefault();
        onClose();
      }}
      onClick={(e) => e.target === ref.current && onClose()}
      aria-label={title}
    >
      <div className="modal-body">
        <button className="modal-close" aria-label="Close" onClick={onClose}>×</button>
        {children}
      </div>
    </dialog>
  );
}
