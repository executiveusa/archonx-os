const statusText = document.getElementById("statusText");
const agentsCount = document.getElementById("agentsCount");
const skillsCount = document.getElementById("skillsCount");
const toolsCount = document.getElementById("toolsCount");
const flywheelCount = document.getElementById("flywheelCount");
const eventsList = document.getElementById("eventsList");
const meetingList = document.getElementById("meetingList");
const taskOutput = document.getElementById("taskOutput");

async function getJson(path) {
  const response = await fetch(path);
  if (!response.ok) {
    throw new Error(`${path} failed (${response.status})`);
  }
  return response.json();
}

function renderList(el, items, empty = "No data") {
  el.innerHTML = "";
  if (!items.length) {
    const li = document.createElement("li");
    li.textContent = empty;
    el.appendChild(li);
    return;
  }
  for (const item of items) {
    const li = document.createElement("li");
    li.textContent = item;
    el.appendChild(li);
  }
}

async function refreshAll() {
  statusText.textContent = "Refreshing";
  try {
    const [agents, skills, tools, flywheel, theater, meetings] = await Promise.all([
      getJson("/api/agents"),
      getJson("/api/skills"),
      getJson("/api/tools"),
      getJson("/api/flywheel"),
      getJson("/api/theater/events?limit=6"),
      getJson("/api/meetings"),
    ]);

    agentsCount.textContent = String(agents.count ?? 0);
    skillsCount.textContent = String(skills.count ?? 0);
    toolsCount.textContent = String((tools.tools ?? []).length);
    flywheelCount.textContent = String(flywheel.backlog_pending ?? 0);

    const events = (theater.events ?? []).map((e) => `${e.type}: ${e.description}`);
    renderList(eventsList, events, "No theater events yet");

    const meetingsData = meetings.meetings ?? meetings.schedule ?? [];
    const meetingsRendered = meetingsData.map((m) => {
      const title = m.title || m.name || m.type || "Meeting";
      const time = m.time || m.scheduled_for || "--:--";
      return `${time} - ${title}`;
    });
    renderList(meetingList, meetingsRendered, "No meetings scheduled");

    statusText.textContent = "Live";
  } catch (error) {
    statusText.textContent = "API error";
    taskOutput.textContent = String(error);
  }
}

async function runSampleTask() {
  statusText.textContent = "Running task";
  const payload = {
    type: "research_deep_dive",
    description: "Summarize one optimization opportunity for the platform",
    crew: "both",
  };
  try {
    const response = await fetch("/api/task", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await response.json();
    taskOutput.textContent = JSON.stringify(data, null, 2);
    await refreshAll();
  } catch (error) {
    taskOutput.textContent = String(error);
    statusText.textContent = "Task failed";
  }
}

document.getElementById("refreshBtn").addEventListener("click", refreshAll);
document.getElementById("sampleTaskBtn").addEventListener("click", runSampleTask);

refreshAll();
