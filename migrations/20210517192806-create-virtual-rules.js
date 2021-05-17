'use strict';
module.exports = {
  up: async (queryInterface, Sequelize) => {
    await queryInterface.createTable('VirtualRules', {
      id: {
        allowNull: false,
        autoIncrement: true,
        primaryKey: true,
        type: Sequelize.INTEGER
      },
      UserName: {
        type: Sequelize.STRING
      },
      Currency: {
        type: Sequelize.STRING
      },
      AllocatedBudget: {
        type: Sequelize.DOUBLE
      },
      BuyPercent: {
        type: Sequelize.DOUBLE
      },
      SellPercent: {
        type: Sequelize.DOUBLE
      },
      StartPrice: {
        type: Sequelize.DOUBLE
      },
      IsActif: {
        type: Sequelize.BOOLEAN
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
    await queryInterface.dropTable('VirtualRules');
  }
};