import { createRouter, createWebHistory } from "vue-router";

import { authGuard } from "./auth";
import AccountView from "../views/AccountView.vue";
import DatasetView from "../views/DatasetView.vue";
import FunctionSelectView from "../views/FunctionSelectView.vue";
import HomeView from "../views/HomeView.vue";
import LoginView from "../views/LoginView.vue";
import MarketView from "../views/MarketView.vue";
import ModelsView from "../views/ModelsView.vue";
import PredictionsView from "../views/PredictionsView.vue";
import PredictionDetailView from "../views/PredictionDetailView.vue";
import RankingView from "../views/RankingView.vue";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", redirect: "/functions" },
    { path: "/login", name: "login", component: LoginView },
    { path: "/functions", name: "functions", component: FunctionSelectView },
    { path: "/home", name: "home", component: HomeView },
    { path: "/datasets", name: "datasets", component: DatasetView },
    { path: "/models", name: "models", component: ModelsView },
    { path: "/predictions", name: "predictions", component: PredictionsView },
    { path: "/predictions/:id", name: "prediction-detail", component: PredictionDetailView },
    { path: "/ranking", name: "ranking", component: RankingView },
    { path: "/market", name: "market", component: MarketView },
    { path: "/account", name: "account", component: AccountView },
  ],
});

router.beforeEach(authGuard);

export default router;
