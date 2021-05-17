'use strict';
module.exports = {
  up: async (queryInterface, Sequelize) => {
    await queryInterface.createTable('Orders', {
      id: {
        allowNull: false,
        autoIncrement: true,
        primaryKey: true,
        type: Sequelize.INTEGER
      },
      UserName: {
        type: Sequelize.STRING
      },
      Way: {
        type: Sequelize.STRING
      },
      Quantity: {
        type: Sequelize.DOUBLE
      },
      Price: {
        type: Sequelize.DOUBLE
      },
      Currency: {
        type: Sequelize.STRING
      },
      From: {
        type: Sequelize.STRING
      },
      State: {
        type: Sequelize.STRING
      },
      createdAt: {
        allowNull: false,
        type: Sequelize.DATE
      },
      updatedAt: {
        allowNull: false,
        type: Sequelize.DATE
      }
    });
  },
  down: async (queryInterface, Sequelize) => {
    await queryInterface.dropTable('Orders');
  }
};