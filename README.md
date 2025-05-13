# MONOFOSM

MONOFOSM (Monoprix Forecasting & Optimization Store Management) is a web application built with Angular 18.0.3 that enables business users to manage store operations intelligently using assistant tools, recommendation systems, and a smart store layout generator.

Link : http://monofosm.com:9600/#/

![MONOFOSM Screenshot](src/assets/layout/images/healthcareCroped.png)

---

## 🌟 Key Features

- 🔒 Role-based dashboard for **Finance**, **Supplier Management**, and **Sales**
- 🤖 **Chatbot assistant** that responds based on user context
- 🧮 **Supplier recommendation** engine based on category data
- 🛍️ **Sales product pairing** suggestion based on purchase correlation
- 🗺️ **Store Layout Generator** with optimization capabilities
- 📊 Real-time interaction with custom grid layout and zone planning
- 🔄 Integrated UI with PrimeNG components and custom dialogs

---

## 🚀 Getting Started

### Prerequisites

Ensure you have the following installed:

- [Node.js](https://nodejs.org/) (version 18+ recommended)
- Angular CLI `npm install -g @angular/cli`

---

## 🔧 Development Server

Run the following command to start the dev server:

```bash
ng serve
```

Navigate to `http://localhost:4200/` in your browser. The app reloads automatically on code changes.

---

## 🧪 Running Tests

### Unit Tests

```bash
ng test

```

Runs unit tests via [Karma](https://karma-runner.github.io/).

### End-to-End Tests

```bash
ng e2e

```

Runs E2E tests using your chosen E2E framework (e.g., Cypress or Protractor).

---

## 🏗️ Building for Production

```bash
ng build

http-server -p 9600 --spa
```

Builds the app for production. Artifacts are stored in the `dist/` folder.



---

## 🧠 Assistant Modules

| Role | Assistant Feature |
| --- | --- |
| Finance | Financial Assistant (Chatbot) |
| Supplier Management | Supplier Recommendation Engine |
| Sales | Product Pairing Recommender & Layout Tool |

---

## 🖼️ Store Layout Generator

The layout generator uses user-defined dimensions and cell sizes to render an editable grid for store planning.

- Supports zone selection and interactive cell editing
- Optimizes layout placement based on selected zone type
- Provides visual feedback using emojis and color indicators

---

## 🧠 ChatBot Panel

The chatbot panel offers:

- Dynamic option and stock-based responses
- Scrollable Q&A history
- Text input and real-time feedback loop

---

## 📡 Live Demo (Optional)

> If hosted online, include the deployed link here:
>

[🔗 Click to Access MONOFOSM Live](https://your-deployed-app-url.com/)

---

## 📚 Further Help

To get more help on Angular CLI:

```bash
ng help

```

Or refer to the [Angular CLI Documentation](https://angular.dev/tools/cli)

---

## 📄 License

This project is for internal demonstration and educational purposes. For usage rights or enterprise deployment, contact the development team.

---

## 👨‍💻 Author & Contributions

Developed by the Skapere Team.

Contributions welcome! Open a pull request or file an issue.
