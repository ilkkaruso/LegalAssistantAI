const path = require("path");
const HtmlWebpackPlugin = require("html-webpack-plugin");
const CopyWebpackPlugin = require("copy-webpack-plugin");

module.exports = {
  mode: process.env.NODE_ENV || "development",
  entry: {
    taskpane: path.resolve(__dirname, "src/taskpane/index.tsx"),
    commands: path.resolve(__dirname, "src/commands/commands.ts"),
  },
  output: {
    path: path.resolve(__dirname, "dist"),
    filename: "[name].js",
    clean: true,
  },
  resolve: {
    extensions: [".ts", ".tsx", ".js"],
  },
  module: {
    rules: [
      {
        test: /\.tsx?$/,
        use: "ts-loader",
        exclude: /node_modules/,
      },
      {
        test: /\.css$/,
        use: ["style-loader", "css-loader"],
      },
    ],
  },
  plugins: [
    new HtmlWebpackPlugin({
      filename: "taskpane.html",
      chunks: ["taskpane"],
      template: path.resolve(__dirname, "src/taskpane/taskpane.html"),
    }),
    new HtmlWebpackPlugin({
      filename: "commands.html",
      chunks: ["commands"],
      template: path.resolve(__dirname, "src/commands/commands.html"),
    }),
    new CopyWebpackPlugin({
      patterns: [
        { from: "manifest.xml", to: "manifest.xml" },
        { from: "assets", to: "assets", noErrorOnMissing: true },
      ],
    }),
  ],
  devServer: {
    static: {
      directory: path.join(__dirname, "dist"),
    },
    port: 3002,
    hot: true,
    https: true,
    headers: {
      "Access-Control-Allow-Origin": "*",
    },
  },
};
