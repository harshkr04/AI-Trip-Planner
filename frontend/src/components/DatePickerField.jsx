import React, { useEffect, useMemo, useRef, useState } from "react";

const WEEKDAYS = ["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"];
const MONTHS = [
  "January",
  "February",
  "March",
  "April",
  "May",
  "June",
  "July",
  "August",
  "September",
  "October",
  "November",
  "December",
];

const formatISODate = (date) => {
  const year = date.getUTCFullYear();
  const month = `${date.getUTCMonth() + 1}`.padStart(2, "0");
  const day = `${date.getUTCDate()}`.padStart(2, "0");
  return `${year}-${month}-${day}`;
};

const parseISODate = (value) => {
  if (!value) return null;
  const parts = value.split("-");
  if (parts.length !== 3) return null;
  const [year, month, day] = parts.map((part) => parseInt(part, 10));
  if (!year || !month || !day) return null;
  const d = new Date(Date.UTC(year, month - 1, day));
  return Number.isNaN(d.getTime()) ? null : d;
};

const formatReadable = (value) => {
  const date = parseISODate(value);
  if (!date) return "";
  return date.toLocaleDateString(undefined, {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
};

const buildMonthMatrix = (viewDate) => {
  const year = viewDate.getFullYear();
  const month = viewDate.getMonth();
  const firstDay = new Date(Date.UTC(year, month, 1));
  const startDay = firstDay.getUTCDay();
  const startDate = new Date(Date.UTC(year, month, 1 - startDay));
  const days = [];
  for (let i = 0; i < 42; i += 1) {
    const d = new Date(startDate);
    d.setUTCDate(startDate.getUTCDate() + i);
    days.push(d);
  }
  return days;
};

export default function DatePickerField({
  value = "",
  onChange = () => {},
  placeholder = "Select date",
  className = "",
  name,
}) {
  const [open, setOpen] = useState(false);
  const [viewDate, setViewDate] = useState(() => parseISODate(value) || new Date());
  const [alignRight, setAlignRight] = useState(false);
  const containerRef = useRef(null);

  const selectedDate = useMemo(() => parseISODate(value), [value]);
  const days = useMemo(() => buildMonthMatrix(viewDate), [viewDate]);

  useEffect(() => {
    if (!open) return;
    const handleClick = (e) => {
      if (!containerRef.current?.contains(e.target)) {
        setOpen(false);
      }
    };
    const handleEsc = (e) => {
      if (e.key === "Escape") setOpen(false);
    };
    document.addEventListener("mousedown", handleClick);
    document.addEventListener("keydown", handleEsc);
    return () => {
      document.removeEventListener("mousedown", handleClick);
      document.removeEventListener("keydown", handleEsc);
    };
  }, [open]);

  useEffect(() => {
    if (!open || !containerRef.current) return;
    const rect = containerRef.current.getBoundingClientRect();
    setAlignRight(rect.left + 320 > window.innerWidth);
  }, [open]);

  useEffect(() => {
    if (!value) return;
    const parsed = parseISODate(value);
    if (parsed) setViewDate(parsed);
  }, [value]);

  const handleSelect = (date) => {
    onChange(formatISODate(date));
    setOpen(false);
  };

  const goMonth = (dir) => {
    setViewDate((prev) => {
      const next = new Date(prev);
      next.setUTCMonth(prev.getUTCMonth() + dir);
      return next;
    });
  };

  return (
    <div className={`date-field ${className}`} ref={containerRef}>
      <input
        type="text"
        name={name}
        value={formatReadable(value)}
        onFocus={() => setOpen(true)}
        onClick={() => setOpen(true)}
        onChange={() => {}}
        placeholder={placeholder}
        readOnly
      />
      <button
        type="button"
        className="date-field__icon"
        aria-label="Open date picker"
        onClick={() => setOpen((prev) => !prev)}
      >
        📅
      </button>

      {open && (
        <div className={`date-popover ${alignRight ? "align-right" : ""}`}>
          <div className="date-popover__head">
            <button type="button" onClick={() => goMonth(-1)} aria-label="Previous month">
              ←
            </button>
            <div className="date-popover__month">
              {MONTHS[viewDate.getMonth()]} {viewDate.getFullYear()}
            </div>
            <button type="button" onClick={() => goMonth(1)} aria-label="Next month">
              →
            </button>
          </div>

          <div className="date-grid">
            {WEEKDAYS.map((day) => (
              <div key={day} className="date-grid__weekday">
                {day}
              </div>
            ))}
            {days.map((day) => {
              const isCurrentMonth = day.getMonth() === viewDate.getMonth();
              const iso = formatISODate(day);
              const isSelected = selectedDate && iso === formatISODate(selectedDate);
              const today = new Date();
              const isToday = iso === formatISODate(today);
              return (
                <button
                  type="button"
                  key={iso}
                  className={[
                    "date-grid__cell",
                    isCurrentMonth ? "" : "date-grid__cell--muted",
                    isSelected ? "date-grid__cell--selected" : "",
                    isToday ? "date-grid__cell--today" : "",
                  ]
                    .filter(Boolean)
                    .join(" ")}
                  onClick={() => handleSelect(day)}
                >
                  {day.getDate()}
                </button>
              );
            })}
          </div>

          <div className="date-popover__footer">
            <button
              type="button"
              onClick={() => {
                onChange("");
                setOpen(false);
              }}
            >
              Clear
            </button>
            <button type="button" onClick={() => handleSelect(new Date())}>
              Today
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

