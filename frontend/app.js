const REFRESH_MS = 2000;

const el = {
  message: document.getElementById("message"),
  partForm: document.getElementById("partForm"),
  partName: document.getElementById("partName"),
  partQty: document.getElementById("partQty"),
  partsBody: document.getElementById("partsBody"),
  orderForm: document.getElementById("orderForm"),
  orderPart: document.getElementById("orderPart"),
  orderQty: document.getElementById("orderQty"),
  ordersBody: document.getElementById("ordersBody"),
};

async function request(url, options = {}) {
  const response = await fetch(url, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(typeof data.detail === "string" ? data.detail : "Invalid input");
  }
  return data;
}

function addCell(row, content) {
  const cell = document.createElement("td");
  if (content instanceof Node) {
    cell.appendChild(content);
  } else {
    cell.textContent = content;
  }
  row.appendChild(cell);
}

function createBadge(status) {
  const badge = document.createElement("span");
  badge.className = `badge ${status}`;
  badge.textContent = status;
  return badge;
}

function createStartButton(order) {
  const button = document.createElement("button");
  button.textContent = "Start";
  button.addEventListener("click", () =>
    perform(() => request(`/orders/${order.id}/start`, { method: "PUT" }))
  );
  return button;
}

function renderParts(parts) {
  el.partsBody.replaceChildren(
    ...parts.map((part) => {
      const row = document.createElement("tr");
      addCell(row, part.name);
      addCell(row, part.quantity);
      return row;
    })
  );

  const selected = el.orderPart.value;
  el.orderPart.replaceChildren(
    ...parts.map((part) => new Option(part.name, part.id))
  );
  if (selected) {
    el.orderPart.value = selected;
  }
}

function renderOrders(orders) {
  el.ordersBody.replaceChildren(
    ...orders.map((order) => {
      const row = document.createElement("tr");
      addCell(row, order.id);
      addCell(row, order.part_name);
      addCell(row, order.quantity);
      addCell(row, createBadge(order.status));
      addCell(row, order.machine || "-");
      addCell(row, order.status === "PENDING" ? createStartButton(order) : "");
      return row;
    })
  );
}

async function refresh() {
  const [parts, orders] = await Promise.all([request("/parts"), request("/orders")]);
  renderParts(parts);
  renderOrders(orders);
}

function showError(error) {
  el.message.textContent = error.message;
}

async function perform(action) {
  el.message.textContent = "";
  try {
    await action();
    await refresh();
  } catch (error) {
    showError(error);
  }
}

el.partForm.addEventListener("submit", (event) => {
  event.preventDefault();
  const body = JSON.stringify({
    name: el.partName.value,
    quantity: Number(el.partQty.value),
  });
  perform(() => request("/parts", { method: "POST", body }));
  el.partForm.reset();
});

el.orderForm.addEventListener("submit", (event) => {
  event.preventDefault();
  const body = JSON.stringify({
    part_id: Number(el.orderPart.value),
    quantity: Number(el.orderQty.value),
  });
  perform(() => request("/orders", { method: "POST", body }));
  el.orderQty.value = "";
});

refresh().catch(showError);
setInterval(() => refresh().catch(showError), REFRESH_MS);